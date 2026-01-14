import { Component, OnDestroy, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { AppSettings } from "../../service/app-settings.service";
import { ResponsiveComponent } from '../../shared';
import { HeaderComponent, FooterComponent } from '../../components';
import { addIcons } from 'ionicons';
import { homeOutline, arrowBackOutline } from 'ionicons/icons';
import { 
  IonContent,
  IonCard, 
  IonCardContent,
  IonButton,
  IonIcon
} from '@ionic/angular/standalone';

@Component({
  selector: "error",
  templateUrl: "./error.html",
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule,
    HeaderComponent,
    FooterComponent,
    IonContent,
    IonCard,
    IonCardContent,
    IonButton,
    IonIcon
  ],
})
export class ErrorPage extends ResponsiveComponent implements OnDestroy {
  constructor(public appSettings: AppSettings) {
    super();
    this.appSettings.appEmpty = true;
    
    // Registrar íconos de Ionic
    addIcons({
      homeOutline,
      arrowBackOutline
    });
  }
  
  getPageTitle(): string {
    return 'Error 404';
  }

  override ngOnDestroy() {
    this.appSettings.appEmpty = false;
  }
}
