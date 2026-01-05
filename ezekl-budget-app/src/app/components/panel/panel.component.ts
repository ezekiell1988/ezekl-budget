import { Component, ViewChild, AfterViewInit, Input } from "@angular/core";
import { CommonModule } from "@angular/common";
import { 
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButton,
  IonIcon,
  IonSpinner
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { 
  expandOutline, 
  refreshOutline, 
  chevronUpOutline,
  chevronDownOutline,
  closeOutline 
} from 'ionicons/icons';
import { ResponsiveComponent } from '../../shared/responsive-component.base';

@Component({
  selector: "panel",
  templateUrl: "./panel.component.html",
  standalone: true,
  imports: [
    CommonModule,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonButton,
    IonIcon,
    IonSpinner
  ],
})
export class PanelComponent extends ResponsiveComponent implements AfterViewInit {
  @ViewChild("panelFooter", { static: false }) panelFooter;
  
  // Inputs para configuración del panel
  @Input() title?: string;
  @Input() variant?: string;
  @Input() noBody: boolean = false;
  @Input() noButton: boolean = false;
  @Input() headerClass?: string;
  @Input() bodyClass?: string;
  @Input() footerClass?: string;
  @Input() panelClass?: string;
  
  // Estado del panel
  expand = false;
  reload = false;
  collapse = false;
  remove = false;
  showFooter = false;

  constructor() {
    super();
    // Registrar íconos de Ionic
    addIcons({
      expandOutline,
      refreshOutline,
      chevronUpOutline,
      chevronDownOutline,
      closeOutline
    });
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.showFooter = this.panelFooter
        ? this.panelFooter.nativeElement &&
          this.panelFooter.nativeElement.children.length > 0
        : false;
    });
  }

  panelExpand() {
    this.expand = !this.expand;
  }
  
  panelReload() {
    this.reload = true;

    setTimeout(() => {
      this.reload = false;
    }, 1500);
  }
  
  panelCollapse() {
    this.collapse = !this.collapse;
  }
  
  panelRemove() {
    this.remove = !this.remove;
  }
}
