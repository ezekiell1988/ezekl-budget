import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DemoWebsocketPage } from './demo-websocket.page';

describe('DemoWebsocketPage', () => {
  let component: DemoWebsocketPage;
  let fixture: ComponentFixture<DemoWebsocketPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(DemoWebsocketPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
