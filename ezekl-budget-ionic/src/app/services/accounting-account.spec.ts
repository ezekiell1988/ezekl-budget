import { TestBed } from '@angular/core/testing';

import { AccountingAccount } from './accounting-account';

describe('AccountingAccount', () => {
  let service: AccountingAccount;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AccountingAccount);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
