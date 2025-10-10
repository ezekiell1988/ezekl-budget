import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { SystemPage } from './system.page';
import { CrmService } from '../../shared/services/crm.service';
import {
  CRMHealthResponse,
  CRMTokenResponse,
  CRMDiagnoseResponse
} from '../../shared/models/crm.models';

describe('SystemPage', () => {
  let component: SystemPage;
  let fixture: ComponentFixture<SystemPage>;
  let crmService: jasmine.SpyObj<CrmService>;

  const mockHealthResponse: CRMHealthResponse = {
    status: 'ok',
    d365: 'https://test.crm.dynamics.com',
    api_version: 'v9.0'
  };

  const mockTokenResponse: CRMTokenResponse = {
    token_preview: 'eyJ0eXAiOiJ...Q4NDAx8A',
    expires_at: 1728481234,
    is_valid: true,
    expires_in_seconds: 3600
  };

  const mockDiagnoseResponse: CRMDiagnoseResponse = {
    environment_variables: {
      CRM_TENANT_ID: 'Configured',
      CRM_CLIENT_ID: 'Configured',
      CRM_D365_BASE_URL: 'Configured'
    },
    token_acquisition: {
      status: 'success',
      message: 'Token obtenido exitosamente'
    },
    d365_connectivity: {
      status: 'success',
      message: 'Conectado a Dynamics 365'
    },
    recommendations: []
  };

  beforeEach(async () => {
    const crmServiceSpy = jasmine.createSpyObj('CrmService', [
      'getHealthCheck',
      'getTokenInfo',
      'getDiagnosis',
      'clearTokenCache'
    ]);

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

    // Setup default spy returns
    crmService.getHealthCheck.and.returnValue(of(mockHealthResponse));
    crmService.getTokenInfo.and.returnValue(of(mockTokenResponse));
    crmService.getDiagnosis.and.returnValue(of(mockDiagnoseResponse));
    crmService.clearTokenCache.and.returnValue(of({ message: 'Cache cleared' }));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load all data on initialization', async () => {
    await component.ngOnInit();

    expect(crmService.getHealthCheck).toHaveBeenCalled();
    expect(crmService.getTokenInfo).toHaveBeenCalled();
    expect(crmService.getDiagnosis).toHaveBeenCalled();
  });

  it('should display health check data', async () => {
    await component.loadHealthCheck();
    fixture.detectChanges();

    expect(component.healthData).toEqual(mockHealthResponse);
    expect(component.healthError).toBeNull();
  });

  it('should display token information', async () => {
    await component.loadTokenInfo();
    fixture.detectChanges();

    expect(component.tokenData).toEqual(mockTokenResponse);
    expect(component.tokenError).toBeNull();
  });

  it('should display diagnosis data', async () => {
    await component.loadDiagnosis();
    fixture.detectChanges();

    expect(component.diagnoseData).toEqual(mockDiagnoseResponse);
    expect(component.diagnoseError).toBeNull();
  });

  it('should handle health check error', async () => {
    const errorMessage = 'Health check failed';
    crmService.getHealthCheck.and.returnValue(
      new (class extends Error {
        constructor() {
          super(errorMessage);
          Object.setPrototypeOf(this, new.target.prototype);
          throw this;
        }
      })() as any
    );

    await component.loadHealthCheck();

    expect(component.healthError).toBeTruthy();
    expect(component.healthData).toBeNull();
  });

  it('should format timestamp correctly', () => {
    const timestamp = 1728481234;
    const formatted = component.formatTimestamp(timestamp);

    expect(formatted).toContain('2024');
  });

  it('should return correct status color', () => {
    expect(component.getStatusColor('ok')).toBe('success');
    expect(component.getStatusColor('success')).toBe('success');
    expect(component.getStatusColor('error')).toBe('danger');
    expect(component.getStatusColor('warning')).toBe('warning');
  });

  it('should return correct status icon', () => {
    expect(component.getStatusIcon('ok')).toBe('checkmarkCircle');
    expect(component.getStatusIcon('success')).toBe('checkmarkCircle');
    expect(component.getStatusIcon('error')).toBe('closeCircle');
    expect(component.getStatusIcon('warning')).toBe('warningOutline');
  });

  it('should clear cache and reload data', async () => {
    spyOn(window, 'alert');

    await component.clearCache();

    expect(crmService.clearTokenCache).toHaveBeenCalled();
    expect(crmService.getHealthCheck).toHaveBeenCalled();
    expect(window.alert).toHaveBeenCalledWith('✅ Caché limpiado exitosamente');
  });

  it('should get object entries for iteration', () => {
    const obj = { key1: 'value1', key2: 'value2' };
    const entries = component.getObjectEntries(obj);

    expect(entries.length).toBe(2);
    expect(entries[0]).toEqual(['key1', 'value1']);
    expect(entries[1]).toEqual(['key2', 'value2']);
  });

  it('should refresh all data on pull to refresh', async () => {
    const mockEvent = { target: { complete: jasmine.createSpy('complete') } };

    await component.onRefresh(mockEvent);

    expect(crmService.getHealthCheck).toHaveBeenCalled();
    expect(crmService.getTokenInfo).toHaveBeenCalled();
    expect(crmService.getDiagnosis).toHaveBeenCalled();
    expect(mockEvent.target.complete).toHaveBeenCalled();
  });

  it('should display system header in the template', async () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    // Esperar a que carguen los datos
    await fixture.whenStable();
    fixture.detectChanges();

    const content = compiled.querySelector('ion-content');
    expect(content).toBeTruthy();
  });

  it('should have proper Ionic structure', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const content = compiled.querySelector('ion-content');
    const cards = compiled.querySelectorAll('ion-card');

    expect(content).toBeTruthy();
    expect(cards.length).toBeGreaterThan(0);
  });
});
