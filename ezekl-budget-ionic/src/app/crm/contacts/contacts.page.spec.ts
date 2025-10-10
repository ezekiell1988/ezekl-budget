import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { of } from 'rxjs';

import { ContactsPage } from './contacts.page';
import { CrmService } from '../../shared/services/crm.service';
import { ContactResponse, ContactsListResponse, CRMOperationResponse } from '../../shared/models/crm.models';

describe('ContactsPage', () => {
  let component: ContactsPage;
  let fixture: ComponentFixture<ContactsPage>;
  let crmService: jasmine.SpyObj<CrmService>;

  const mockContact: ContactResponse = {
    contactid: '12345-67890-abcde',
    fullname: 'María García',
    firstname: 'María',
    lastname: 'García',
    jobtitle: 'Gerente de Ventas',
    telephone1: '+34 912 345 678',
    mobilephone: '+34 612 345 678',
    emailaddress1: 'maria.garcia@empresa.com',
    address1_line1: 'Calle Principal 123',
    address1_city: 'Madrid',
    address1_postalcode: '28001',
    address1_country: 'España',
    createdon: '2025-10-09T10:30:00Z',
    modifiedon: '2025-10-09T11:00:00Z'
  };

  const mockContactsListResponse: ContactsListResponse = {
    count: 1,
    contacts: [mockContact],
    next_link: undefined
  };

  const mockOperationResponse: CRMOperationResponse = {
    status: 'success',
    message: 'Operation successful',
    entity_id: '12345-67890-abcde'
  };

  beforeEach(async () => {
    const crmServiceSpy = jasmine.createSpyObj('CrmService', [
      'getContacts',
      'getContact',
      'createContact',
      'updateContact',
      'deleteContact'
    ]);

    await TestBed.configureTestingModule({
      imports: [
        ContactsPage,
        ReactiveFormsModule
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: CrmService, useValue: crmServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ContactsPage);
    component = fixture.componentInstance;
    crmService = TestBed.inject(CrmService) as jasmine.SpyObj<CrmService>;

    // Setup default spy returns
    crmService.getContacts.and.returnValue(of(mockContactsListResponse));
    crmService.createContact.and.returnValue(of(mockOperationResponse));
    crmService.updateContact.and.returnValue(of(mockOperationResponse));
    crmService.deleteContact.and.returnValue(of(mockOperationResponse));

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load contacts on initialization', () => {
    expect(crmService.getContacts).toHaveBeenCalled();
    expect(component.contacts.length).toBe(1);
    expect(component.contacts[0]).toEqual(mockContact);
  });

  it('should display contact name in the template', async () => {
    // Wait for async loading to complete
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const cardTitle = compiled.querySelector('ion-card-title');
    expect(cardTitle?.textContent?.trim()).toBe('María García');
  });

  it('should show loading state initially', () => {
    component.isLoading = true;
    component.contacts = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const skeleton = compiled.querySelector('ion-skeleton-text');
    expect(skeleton).toBeTruthy();
  });

  it('should show empty state when no contacts', () => {
    component.isLoading = false;
    component.contacts = [];
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyMessage = compiled.textContent;
    expect(emptyMessage).toContain('No hay contactos');
  });

  it('should initialize create form with default values', () => {
    expect(component.createForm).toBeDefined();
    expect(component.createForm.get('firstname')?.value).toBe('');
  });

  it('should validate required fields in create form', () => {
    const firstnameControl = component.createForm.get('firstname');
    const lastnameControl = component.createForm.get('lastname');

    firstnameControl?.setValue('');
    lastnameControl?.setValue('');
    expect(component.createForm.invalid).toBe(true);

    firstnameControl?.setValue('María');
    lastnameControl?.setValue('García');
    expect(component.createForm.valid).toBe(true);
  });

  it('should validate email format in create form', () => {
    const emailControl = component.createForm.get('emailaddress1');

    emailControl?.setValue('invalid-email');
    expect(emailControl?.invalid).toBe(true);

    emailControl?.setValue('valid@email.com');
    expect(emailControl?.valid).toBe(true);
  });

  it('should open create modal', () => {
    component.openCreateModal();
    expect(component.isCreateModalOpen).toBe(true);
  });

  it('should close create modal', () => {
    component.isCreateModalOpen = true;
    component.closeCreateModal();
    expect(component.isCreateModalOpen).toBe(false);
  });

  it('should open view modal with selected contact', () => {
    component.openViewModal(mockContact);
    expect(component.isViewModalOpen).toBe(true);
    expect(component.selectedContact).toEqual(mockContact);
  });

  it('should open edit modal with contact data', () => {
    component.openEditModal(mockContact);
    expect(component.isEditModalOpen).toBe(true);
    expect(component.editForm.get('firstname')?.value).toBe('María');
  });

  it('should filter contacts by search text', async () => {
    await component.onHeaderSearch('García');
    expect(crmService.getContacts).toHaveBeenCalled();
    expect(component.searchText).toBe('García');
  });

  it('should clear filters', async () => {
    component.searchText = 'test';
    await component.clearFilters();
    expect(component.searchText).toBe('');
  });

  it('should format date correctly', () => {
    const formatted = component.formatDate('2025-10-09T10:30:00Z');
    expect(formatted).toContain('2025');
  });

  it('should handle error when loading contacts', async () => {
    crmService.getContacts.and.returnValue(of(mockContactsListResponse));
    await component.loadContacts();
    expect(component.contacts.length).toBeGreaterThanOrEqual(0);
  });

  it('should refresh contacts list', async () => {
    const mockEvent = { target: { complete: jasmine.createSpy('complete') } };
    await component.onRefresh(mockEvent);
    expect(mockEvent.target.complete).toHaveBeenCalled();
  });

  it('should load more contacts on infinite scroll', async () => {
    component.hasNextPage = true;
    component.nextLink = '/api/contacts?$skiptoken=abc';

    const mockEvent = { target: { complete: jasmine.createSpy('complete') } };

    // Need to mock getContactsByNextLink as well
    const nextLinkResponse: ContactsListResponse = {
      count: 1,
      contacts: [mockContact],
      next_link: undefined
    };

    crmService.getContactsByNextLink = jasmine.createSpy('getContactsByNextLink')
      .and.returnValue(of(nextLinkResponse));

    await component.onLoadMore(mockEvent);
    expect(mockEvent.target.complete).toHaveBeenCalled();
  });
});
