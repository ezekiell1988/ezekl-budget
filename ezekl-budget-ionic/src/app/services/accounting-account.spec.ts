import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { AccountingAccountService } from './accounting-account';

describe('AccountingAccountService', () => {
  let service: AccountingAccountService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(AccountingAccountService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
