import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { AzureOpenAIToolsService } from './azure-openai-tools.service';

describe('AzureOpenAIToolsService', () => {
  let service: AzureOpenAIToolsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AzureOpenAIToolsService]
    });
    service = TestBed.inject(AzureOpenAIToolsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should have at least one tool available', () => {
    const tools = service.getAvailableTools();
    expect(tools.length).toBeGreaterThan(0);
  });

  it('should have get_accounting_accounts tool', () => {
    const tool = service.getToolByName('get_accounting_accounts');
    expect(tool).toBeTruthy();
    expect(tool?.name).toBe('get_accounting_accounts');
  });
});
