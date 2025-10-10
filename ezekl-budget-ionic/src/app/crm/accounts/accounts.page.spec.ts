import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { of } from 'rxjs';

import { AccountsPage } from './accounts.page';
import { CrmService } from '../../shared/services/crm.service';
import { AccountResponse, AccountsListResponse, CRMOperationResponse } from '../../shared/models/crm.models';

describe('AccountsPage', () => {
  let component: AccountsPage;
  let fixture: ComponentFixture<AccountsPage>;
  let crmService: jasmine.SpyObj<CrmService>;

  const mockAccount: AccountResponse = {
    accountid: '12345-67890-abcde',
    name: 'Test Company',
    accountnumber: 'ACC-001',
    telephone1: '+34 912 345 678',
    emailaddress1: 'contact@test.com',
    websiteurl: 'https://www.test.com',
    address1_line1: 'Calle Principal 123',
    address1_city: 'Madrid',
    address1_postalcode: '28001',
    address1_country: 'España',
    createdon: '2025-10-09T10:30:00Z',
    modifiedon: '2025-10-09T11:00:00Z'
  };

  const mockAccountsListResponse: AccountsListResponse = {
    count: 1,
    accounts: [mockAccount],
    next_link: undefined
  };

  const mockOperationResponse: CRMOperationResponse = {
    status: 'success',
    message: 'Operation successful',
    entity_id: '12345-67890-abcde'
  };

  beforeEach(async () => {
    const crmServiceSpy = jasmine.createSpyObj('CrmService', [
      'getAccounts',
      'getAccount',
      'createAccount',
      'updateAccount',
      'deleteAccount'
    ]);

    await TestBed.configureTestingModule({
      imports: [
        AccountsPage,
        ReactiveFormsModule
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: CrmService, useValue: crmServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AccountsPage);
    component = fixture.componentInstance;
    crmService = TestBed.inject(CrmService) as jasmine.SpyObj<CrmService>;

    // Setup default spy returns
    crmService.getAccounts.and.returnValue(of(mockAccountsListResponse));
    crmService.createAccount.and.returnValue(of(mockOperationResponse));
    crmService.updateAccount.and.returnValue(of(mockOperationResponse));
    crmService.deleteAccount.and.returnValue(of(mockOperationResponse));

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load accounts on initialization', () => {
    expect(crmService.getAccounts).toHaveBeenCalled();
    expect(component.accounts.length).toBe(1);
    expect(component.accounts[0]).toEqual(mockAccount);
  });

  it('should display account name in the template', async () => {
    // Wait for async loading to complete
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const accountTitle = compiled.querySelector('ion-card-title');
    expect(accountTitle?.textContent?.trim()).toBe('Test Company');
  });

  it('should show loading state initially', () => {
    component.isLoading = true;
    component.accounts = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const skeletons = compiled.querySelectorAll('ion-skeleton-text');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should show empty state when no accounts', () => {
    component.isLoading = false;
    component.accounts = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyText = compiled.querySelector('h3');
    expect(emptyText?.textContent).toContain('No hay cuentas');
  });

  it('should initialize create form with default values', () => {
    expect(component.createForm.get('name')?.value).toBe('');
    expect(component.createForm.get('telephone1')?.value).toBe('');
  });

  it('should validate required fields in create form', () => {
    const nameControl = component.createForm.get('name');

    // Test empty name
    nameControl?.setValue('');
    expect(nameControl?.invalid).toBeTruthy();
    expect(nameControl?.errors?.['required']).toBeTruthy();

    // Test valid name
    nameControl?.setValue('Valid Company Name');
    expect(nameControl?.valid).toBeTruthy();
  });

  it('should validate email format in create form', () => {
    const emailControl = component.createForm.get('emailaddress1');

    // Test invalid email
    emailControl?.setValue('invalid-email');
    expect(emailControl?.invalid).toBeTruthy();
    expect(emailControl?.errors?.['email']).toBeTruthy();

    // Test valid email
    emailControl?.setValue('valid@email.com');
    expect(emailControl?.valid).toBeTruthy();
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

  it('should open view modal with selected account', () => {
    component.openViewModal(mockAccount);
    expect(component.isViewModalOpen).toBeTruthy();
    expect(component.selectedAccount).toEqual(mockAccount);
  });

  it('should open edit modal with account data', () => {
    component.openEditModal(mockAccount);
    expect(component.isEditModalOpen).toBeTruthy();
    expect(component.editForm.get('name')?.value).toBe(mockAccount.name);
  });

  it('should filter accounts by search text', async () => {
    await component.onHeaderSearch('test');
    expect(component.searchText).toBe('test');
    expect(crmService.getAccounts).toHaveBeenCalledWith(jasmine.objectContaining({
      filter_query: "contains(name,'test')"
    }));
  });

  it('should clear filters', async () => {
    component.searchText = 'test';
    await component.clearFilters();
    expect(component.searchText).toBe('');
    expect(crmService.getAccounts).toHaveBeenCalled();
  });

  it('should format date correctly', () => {
    const formattedDate = component.formatDate('2025-10-09T10:30:00Z');
    expect(formattedDate).toContain('oct');
    expect(formattedDate).toContain('2025');
  });

  it('should handle error when loading accounts', async () => {
    crmService.getAccounts.and.returnValue(of(mockAccountsListResponse));
    await component.loadAccounts();
    expect(component.isLoading).toBeFalsy();
  });

  it('should refresh accounts list', async () => {
    const mockEvent = { target: { complete: jasmine.createSpy('complete') } };
    await component.onRefresh(mockEvent);
    expect(crmService.getAccounts).toHaveBeenCalled();
    expect(mockEvent.target.complete).toHaveBeenCalled();
  });

  it('should load more accounts on infinite scroll', async () => {
    component.hasNextPage = true;
    const mockEvent = { target: { complete: jasmine.createSpy('complete') } };

    await component.onLoadMore(mockEvent);
    expect(component.currentPage).toBe(2);
    expect(mockEvent.target.complete).toHaveBeenCalled();
  });
});
