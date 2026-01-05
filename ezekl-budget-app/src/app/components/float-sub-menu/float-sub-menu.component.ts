import { Component, Input, Output, EventEmitter } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { AppSettings } from "../../service/app-settings.service";
import { ResponsiveComponent } from '../../shared/responsive-component.base';

declare var slideToggle: any;

@Component({
  selector: "float-sub-menu",
  templateUrl: "./float-sub-menu.component.html",
  standalone: true,
  imports: [CommonModule, RouterModule],
})
export class FloatSubMenuComponent extends ResponsiveComponent {
  @Input() menus;
  @Input() top;
  @Input() left;
  @Input() right;
  @Input() bottom;
  @Input() lineTop;
  @Input() lineBottom;
  @Input() arrowTop;
  @Input() arrowBottom;

  @Output() remainAppSidebarFloatSubMenu = new EventEmitter();
  @Output() hideAppSidebarFloatSubMenu = new EventEmitter();
  @Output() calculateFloatSubMenuPosition = new EventEmitter();

  constructor(public appSettings: AppSettings) {
    super();
  }

  expandCollapseSubmenu(e, currentMenu, allMenu, active) {
    e.preventDefault();
    var targetItem = e.target.closest(".menu-item");
    var target = <HTMLElement>targetItem.querySelector(".menu-submenu");
    slideToggle(target);
    this.calculateFloatSubMenuPosition.emit();
  }

  remainMenu() {
    this.remainAppSidebarFloatSubMenu.emit(true);
  }

  hideMenu() {
    this.hideAppSidebarFloatSubMenu.emit(true);
  }
}
