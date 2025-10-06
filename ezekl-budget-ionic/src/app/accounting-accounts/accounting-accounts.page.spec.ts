import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AccountingAccountsPage } from './accounting-accounts.page';

describe('AccountingAccountsPage', () => {
  let component: AccountingAccountsPage;
  let fixture: ComponentFixture<AccountingAccountsPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountingAccountsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
