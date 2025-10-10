import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { SystemPage } from './system.page';
import { CrmService } from '../../shared/services/crm.service';

describe('SystemPage', () => {
  let component: SystemPage;
  let fixture: ComponentFixture<SystemPage>;
  let crmService: jasmine.SpyObj<CrmService>;

  beforeEach(async () => {
    const crmServiceSpy = jasmine.createSpyObj('CrmService', ['getSystemInfo']);

    await TestBed.configureTestingModule({
      imports: [
        SystemPage
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: CrmService, useValue: crmServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SystemPage);
    component = fixture.componentInstance;
    crmService = TestBed.inject(CrmService) as jasmine.SpyObj<CrmService>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display system header in the template', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const header = compiled.querySelector('ion-header ion-toolbar ion-title');
    expect(header?.textContent?.trim()).toBe('Sistema');
  });

  it('should display under development message', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const content = compiled.querySelector('ion-content');
    expect(content?.textContent).toContain('En desarrollo...');
  });

  it('should display system placeholder content', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const paragraphs = compiled.querySelectorAll('p');

    expect(paragraphs.length).toBeGreaterThan(0);
    expect(paragraphs[0].textContent).toContain('En desarrollo...');
  });

  it('should have proper Ionic structure', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    const header = compiled.querySelector('ion-header');
    const toolbar = compiled.querySelector('ion-toolbar');
    const title = compiled.querySelector('ion-title');
    const content = compiled.querySelector('ion-content');

    expect(header).toBeTruthy();
    expect(toolbar).toBeTruthy();
    expect(title).toBeTruthy();
    expect(content).toBeTruthy();
  });

  it('should have correct page title', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const title = compiled.querySelector('ion-title');
    expect(title?.textContent?.trim()).toBe('Sistema');
  });
});
