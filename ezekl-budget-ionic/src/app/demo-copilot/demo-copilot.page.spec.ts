import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DemoCopilotPage } from './demo-copilot.page';

describe('DemoCopilotPage', () => {
  let component: DemoCopilotPage;
  let fixture: ComponentFixture<DemoCopilotPage>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [DemoCopilotPage],
    }).compileComponents();

    fixture = TestBed.createComponent(DemoCopilotPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
