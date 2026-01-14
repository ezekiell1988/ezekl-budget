import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MenuStateService {
  private sidebarMenuOpen$ = new BehaviorSubject<boolean>(false);

  constructor() {}

  setSidebarMenuState(isOpen: boolean): void {
    this.sidebarMenuOpen$.next(isOpen);
  }

  getSidebarMenuState(): Observable<boolean> {
    return this.sidebarMenuOpen$.asObservable();
  }

  isSidebarMenuOpen(): boolean {
    return this.sidebarMenuOpen$.value;
  }
}
