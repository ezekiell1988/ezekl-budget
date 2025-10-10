import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { Location } from '@angular/common';
import { provideRouter } from '@angular/router';

import { CrmPage } from './crm.page';

describe('CrmPage', () => {
  let component: CrmPage;
  let fixture: ComponentFixture<CrmPage>;
  let router: Router;
  let location: Location;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrmPage],
      providers: [
        provideRouter([
          { path: 'crm', component: CrmPage },
          { path: 'crm/cases', redirectTo: 'crm' },
          { path: 'crm/accounts', redirectTo: 'crm' },
          { path: 'crm/contacts', redirectTo: 'crm' },
          { path: 'crm/system', redirectTo: 'crm' }
        ])
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(CrmPage);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    location = TestBed.inject(Location);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render CRM title in header', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const header = compiled.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should display all tab buttons', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const tabButtons = compiled.querySelectorAll('ion-tab-button');

    expect(tabButtons.length).toBe(4);
    expect(tabButtons[0].getAttribute('routerLink')).toBe('/crm/cases');
    expect(tabButtons[1].getAttribute('routerLink')).toBe('/crm/accounts');
    expect(tabButtons[2].getAttribute('routerLink')).toBe('/crm/contacts');
    expect(tabButtons[3].getAttribute('routerLink')).toBe('/crm/system');
  });

  it('should have router-outlet for tab content', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const routerOutlet = compiled.querySelector('router-outlet');
    expect(routerOutlet).toBeTruthy();
  });

  it('should have correct icons for each tab', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const icons = compiled.querySelectorAll('ion-icon');

    expect(icons.length).toBe(4);
    expect(icons[0].getAttribute('name')).toBe('document-text-outline');
    expect(icons[1].getAttribute('name')).toBe('business-outline');
    expect(icons[2].getAttribute('name')).toBe('person-outline');
    expect(icons[3].getAttribute('name')).toBe('medical-outline');
  });

  it('should have correct tab labels', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const labels = compiled.querySelectorAll('ion-label');

    expect(labels.length).toBe(4);
    expect(labels[0].textContent?.trim()).toBe('Casos');
    expect(labels[1].textContent?.trim()).toBe('Cuentas');
    expect(labels[2].textContent?.trim()).toBe('Contactos');
    expect(labels[3].textContent?.trim()).toBe('Sistema');
  });
});
