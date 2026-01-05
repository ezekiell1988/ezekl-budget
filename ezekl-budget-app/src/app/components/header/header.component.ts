import {
  Component,
  Input,
  Output,
  EventEmitter,
  Renderer2,
  OnDestroy,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { AppSettings } from "../../service/app-settings.service";
import { ResponsiveComponent } from '../../shared/responsive-component.base';

declare var slideToggle: any;

@Component({
  selector: "header",
  templateUrl: "./header.component.html",
  standalone: true,
  imports: [CommonModule],
})
export class HeaderComponent extends ResponsiveComponent implements OnDestroy {
  @Input() appSidebarTwo;
  @Output() appSidebarEndToggled = new EventEmitter<boolean>();
  @Output() appSidebarMobileToggled = new EventEmitter<boolean>();
  @Output() appSidebarEndMobileToggled = new EventEmitter<boolean>();

  toggleAppSidebarMobile() {
    this.appSidebarMobileToggled.emit(true);
  }

  toggleAppSidebarEnd() {
    this.appSidebarEndToggled.emit(true);
  }

  toggleAppSidebarEndMobile() {
    this.appSidebarEndMobileToggled.emit(true);
  }

  toggleAppTopMenuMobile() {
    var target = document.querySelector(".app-top-menu");
    if (target) {
      slideToggle(target);
    }
  }

  toggleAppHeaderMegaMenuMobile() {
    this.appSettings.appHeaderMegaMenuMobileToggled =
      !this.appSettings.appHeaderMegaMenuMobileToggled;
  }

  override ngOnDestroy() {
    this.appSettings.appHeaderMegaMenuMobileToggled = false;
    super.ngOnDestroy();
  }

  constructor(private renderer: Renderer2, public appSettings: AppSettings) {
    super();
  }
}
