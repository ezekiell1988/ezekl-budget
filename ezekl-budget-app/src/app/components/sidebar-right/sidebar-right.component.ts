import { Component, Output, EventEmitter } from "@angular/core";
import { CommonModule } from "@angular/common";
import { NgScrollbarModule } from "ngx-scrollbar";
import { ResponsiveComponent } from '../../shared/responsive-component.base';

@Component({
  selector: "sidebar-right",
  templateUrl: "./sidebar-right.component.html",
  standalone: true,
  imports: [CommonModule, NgScrollbarModule],
})
export class SidebarRightComponent extends ResponsiveComponent {
  @Output() appSidebarEndMobileToggled = new EventEmitter<boolean>();

  constructor() {
    super();
  }

  toggleAppSidebarEndMobile() {
    this.appSidebarEndMobileToggled.emit(true);
  }
}
