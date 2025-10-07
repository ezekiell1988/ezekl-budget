import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DemoRealtimePage } from './demo-realtime.page';

describe('DemoRealtimePage', () => {
  let component: DemoRealtimePage;
  let fixture: ComponentFixture<DemoRealtimePage>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [DemoRealtimePage],
    }).compileComponents();

    fixture = TestBed.createComponent(DemoRealtimePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
