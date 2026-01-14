import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { 
  IonFooter,
  IonToolbar,
  IonTitle
} from '@ionic/angular/standalone';
import { AppSettings } from '../../service/app-settings.service';
import { ResponsiveComponent } from '../../shared/responsive-component.base';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  standalone: true,
  imports: [
    CommonModule,
    IonFooter,
    IonToolbar,
    IonTitle
  ],
})
export class FooterComponent extends ResponsiveComponent {
  @Input() footerText = '';
  @Input() color = 'theme'; // Color del toolbar para versión móvil
  @Input() translucent = false; // Para footer translúcido en iOS

  constructor(public appSettings: AppSettings) {
    super();
    
    // Si no se proporciona texto, usar el del appSettings
    if (!this.footerText) {
      this.footerText = `© ${this.appSettings.nameCompany} BackOffice`;
    }
  }
}
