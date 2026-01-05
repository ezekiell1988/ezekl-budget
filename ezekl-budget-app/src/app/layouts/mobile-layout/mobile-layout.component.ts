import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { 
  IonApp,
  IonContent
} from '@ionic/angular/standalone';
import { HeaderComponent, SidebarComponent } from '../../components';

@Component({
  selector: 'app-mobile-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    IonApp,
    IonContent,
    HeaderComponent,
    SidebarComponent
  ],
  templateUrl: './mobile-layout.component.html',
  styleUrls: ['./mobile-layout.component.scss']
})
export class MobileLayoutComponent {
  pageTitle = 'EzekL Budget';

  constructor() {}
}
