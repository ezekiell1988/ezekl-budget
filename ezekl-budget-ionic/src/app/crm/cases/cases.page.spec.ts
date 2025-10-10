import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

import { CasesPage } from './cases.page';
import { CrmService } from '../../shared/services/crm.service';
import {
  CaseResponse,
  CasesListResponse,
  CRMOperationResponse,
  CaseStatus,
  CasePriority
} from '../../shared/models/crm.models';

describe('CasesPage', () => {
  let component: CasesPage;
  let fixture: ComponentFixture<CasesPage>;
  let crmService: jasmine.SpyObj<CrmService>;

  const mockCase: CaseResponse = {
    incidentid: '12345-67890-abcde',
    title: 'Test Case',
    description: 'Test description',
    statuscode: CaseStatus.Active,
    prioritycode: CasePriority.Normal,
    createdon: '2025-10-09T10:30:00Z',
    modifiedon: '2025-10-09T11:00:00Z',
    customer_name: 'Test Customer'
  };

  const mockCasesListResponse: CasesListResponse = {
    count: 1,
    cases: [mockCase],
    next_link: undefined
  };

  const mockOperationResponse: CRMOperationResponse = {
    status: 'success',
    message: 'Operation successful',
    entity_id: '12345-67890-abcde'
  };

  beforeEach(async () => {
    const crmServiceSpy = jasmine.createSpyObj('CrmService', [
      'getCases',
      'getCase',
      'createCase',
      'updateCase',
      'deleteCase'
    ]);

    await TestBed.configureTestingModule({
      imports: [
        CasesPage,
        ReactiveFormsModule
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: CrmService, useValue: crmServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(CasesPage);
    component = fixture.componentInstance;
    crmService = TestBed.inject(CrmService) as jasmine.SpyObj<CrmService>;

    // Setup default spy returns
    crmService.getCases.and.returnValue(of(mockCasesListResponse));
    crmService.createCase.and.returnValue(of(mockOperationResponse));
    crmService.updateCase.and.returnValue(of(mockOperationResponse));
    crmService.deleteCase.and.returnValue(of(mockOperationResponse));

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load cases on initialization', () => {
    expect(crmService.getCases).toHaveBeenCalled();
    expect(component.cases.length).toBe(1);
    expect(component.cases[0]).toEqual(mockCase);
  });

  it('should display case title in the template', async () => {
    // Wait for async loading to complete
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const caseTitle = compiled.querySelector('ion-card-title');
    expect(caseTitle?.textContent?.trim()).toBe('Test Case');
  });

  it('should show loading state initially', () => {
    component.isLoading = true;
    component.cases = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const loadingContainer = compiled.querySelector('.loading-container');
    expect(loadingContainer).toBeTruthy();
  });

  it('should show empty state when no cases', () => {
    component.isLoading = false;
    component.cases = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyContainer = compiled.querySelector('.empty-container');
    expect(emptyContainer).toBeTruthy();
    expect(emptyContainer?.textContent).toContain('No hay casos');
  });

  it('should initialize create form with default values', () => {
    expect(component.createForm.get('prioritycode')?.value).toBe(CasePriority.Normal);
    expect(component.createForm.get('title')?.value).toBe('');
  });

  it('should validate required fields in create form', () => {
    const titleControl = component.createForm.get('title');

    // Test empty title
    titleControl?.setValue('');
    expect(titleControl?.invalid).toBeTruthy();
    expect(titleControl?.errors?.['required']).toBeTruthy();

    // Test title too short
    titleControl?.setValue('abc');
    expect(titleControl?.invalid).toBeTruthy();
    expect(titleControl?.errors?.['minlength']).toBeTruthy();

    // Test valid title
    titleControl?.setValue('Valid case title');
    expect(titleControl?.valid).toBeTruthy();
  });

  it('should open create modal', () => {
    component.openCreateModal();
    expect(component.isCreateModalOpen).toBeTruthy();
  });

  it('should close create modal', () => {
    component.isCreateModalOpen = true;
    component.closeCreateModal();
    expect(component.isCreateModalOpen).toBeFalsy();
  });

  it('should open view modal with selected case', () => {
    component.openViewModal(mockCase);
    expect(component.isViewModalOpen).toBeTruthy();
    expect(component.selectedCase).toEqual(mockCase);
  });

  it('should open edit modal with case data', () => {
    component.openEditModal(mockCase);
    expect(component.isEditModalOpen).toBeTruthy();
    expect(component.selectedCase).toEqual(mockCase);
    expect(component.editForm.get('title')?.value).toBe(mockCase.title);
  });

  it('should filter cases by search text', async () => {
    component.searchText = 'test';
    await component.onSearch({ target: { value: 'test' } });

    expect(crmService.getCases).toHaveBeenCalledWith(
      jasmine.objectContaining({
        filter_query: jasmine.stringContaining("contains(title,'test')")
      })
    );
  });

  it('should filter cases by status', async () => {
    await component.onStatusFilter({ target: { value: CaseStatus.Active } });

    expect(component.selectedStatus).toBe(CaseStatus.Active);
    expect(crmService.getCases).toHaveBeenCalledWith(
      jasmine.objectContaining({
        filter_query: jasmine.stringContaining(`statuscode eq ${CaseStatus.Active}`)
      })
    );
  });

  it('should clear filters', async () => {
    component.searchText = 'test';
    component.selectedStatus = CaseStatus.Active;

    await component.clearFilters();

    expect(component.searchText).toBe('');
    expect(component.selectedStatus).toBeNull();
  });

  it('should get correct status text', () => {
    expect(component.getStatusText(CaseStatus.Active)).toBe('Activo');
    expect(component.getStatusText(CaseStatus.Resolved)).toBe('Resuelto');
    expect(component.getStatusText(CaseStatus.Canceled)).toBe('Cancelado');
    expect(component.getStatusText(undefined)).toBe('Desconocido');
  });

  it('should get correct status color', () => {
    expect(component.getStatusColor(CaseStatus.Active)).toBe('primary');
    expect(component.getStatusColor(CaseStatus.Resolved)).toBe('success');
    expect(component.getStatusColor(CaseStatus.Canceled)).toBe('medium');
  });

  it('should get correct priority text', () => {
    expect(component.getPriorityText(CasePriority.High)).toBe('Alta');
    expect(component.getPriorityText(CasePriority.Normal)).toBe('Normal');
    expect(component.getPriorityText(CasePriority.Low)).toBe('Baja');
  });

  it('should format date correctly', () => {
    const testDate = '2025-10-09T10:30:00Z';
    const formatted = component.formatDate(testDate);
    expect(formatted).toContain('9 oct 2025');
    expect(formatted).toContain('10:30');
  });

  it('should handle error when loading cases', async () => {
    const errorMessage = 'Network error';
    crmService.getCases.and.returnValue(throwError(() => new Error(errorMessage)));

    spyOn(component, 'showErrorToast' as any);

    await component.loadCases();

    expect((component as any).showErrorToast).toHaveBeenCalledWith(`Error cargando casos: Error: ${errorMessage}`);
  });

  it('should refresh cases list', async () => {
    const event = { target: { complete: jasmine.createSpy('complete') } };

    await component.onRefresh(event);

    expect(crmService.getCases).toHaveBeenCalled();
    expect(event.target.complete).toHaveBeenCalled();
    expect(component.currentPage).toBe(1);
  });

  it('should load more cases on infinite scroll', async () => {
    const event = { target: { complete: jasmine.createSpy('complete') } };
    component.currentPage = 1;

    await component.onLoadMore(event);

    expect(component.currentPage).toBe(2);
    expect(component.isLoadingMore).toBeFalsy();
    expect(event.target.complete).toHaveBeenCalled();
  });
});
