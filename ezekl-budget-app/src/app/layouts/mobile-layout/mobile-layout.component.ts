import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { 
  IonApp, 
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonMenu,
  IonMenuButton,
  IonButtons,
  IonButton,
  IonIcon,
  IonList,
  IonItem,
  IonLabel,
  IonMenuToggle
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { 
  homeOutline, 
  personOutline, 
  settingsOutline, 
  menuOutline,
  logOutOutline,
  walletOutline,
  statsChartOutline,
  documentTextOutline,
  businessOutline,
  notificationsOutline
} from 'ionicons/icons';
import { AppMenuService } from '../../service/app-menus.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-mobile-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    IonApp,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonMenu,
    IonMenuButton,
    IonButtons,
    IonButton,
    IonIcon,
    IonList,
    IonItem,
    IonLabel,
    IonMenuToggle
  ],
  template: `
    <ion-app>
      <!-- Menú lateral de Ionic -->
      <ion-menu contentId="main-content" menuId="main-menu" type="overlay">
        <ion-header>
          <ion-toolbar>
            <ion-title>Menú</ion-title>
          </ion-toolbar>
        </ion-header>
        <ion-content>
          <ion-list>
            @for (item of menuItems; track item.title) {
              <ion-menu-toggle auto-hide="true">
                <ion-item 
                  [routerLink]="item.url" 
                  routerLinkActive="selected"
                  [detail]="false"
                  lines="none">
                  <ion-icon [name]="item.icon" slot="start"></ion-icon>
                  <ion-label>{{ item.title }}</ion-label>
                </ion-item>
              </ion-menu-toggle>
            }
          </ion-list>
          
          <div class="menu-footer">
            <ion-item lines="none" button (click)="logout()">
              <ion-icon name="log-out-outline" slot="start"></ion-icon>
              <ion-label>Cerrar Sesión</ion-label>
            </ion-item>
          </div>
        </ion-content>
      </ion-menu>

      <!-- Contenido principal -->
      <div class="ion-page" id="main-content">
        <!-- Header de la app móvil -->
        <ion-header>
          <ion-toolbar>
            <ion-buttons slot="start">
              <ion-menu-button></ion-menu-button>
            </ion-buttons>
            <ion-title>{{ pageTitle }}</ion-title>
            <ion-buttons slot="end">
              <ion-button>
                <ion-icon name="notifications-outline"></ion-icon>
              </ion-button>
            </ion-buttons>
          </ion-toolbar>
        </ion-header>

        <!-- Contenido - donde se renderizan las páginas -->
        <ion-content>
          <router-outlet></router-outlet>
        </ion-content>
      </div>
    </ion-app>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .selected {
      --background: var(--ion-color-primary-tint);
      --color: var(--ion-color-primary);
    }

    .menu-footer {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 16px;
      border-top: 1px solid var(--ion-border-color);
    }

    ion-content {
      --background: var(--ion-background-color);
      --padding-start: 0;
      --padding-end: 0;
      --padding-top: 0;
      --padding-bottom: 0;
    }
    
    .ion-page {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
  `]
})
export class MobileLayoutComponent implements OnInit, OnDestroy {
  pageTitle = 'EzekL Budget';
  
  menuItems: Array<{ title: string; url: string; icon: string }> = [];
  tabItems: Array<{ title: string; url: string; icon: string }> = [];
  
  private menuSubscription: Subscription | null = null;

  constructor(private appMenuService: AppMenuService) {
    // Registrar íconos de Ionicons
    addIcons({
      homeOutline,
      personOutline,
      settingsOutline,
      menuOutline,
      logOutOutline,
      walletOutline,
      statsChartOutline,
      documentTextOutline,
      businessOutline,
      notificationsOutline
    });
  }

  ngOnInit(): void {
    this.loadMenuItems();
    this.setupTabItems();
  }

  private loadMenuItems(): void {
    // Convertir el menú de color-admin a formato Ionic
    const menus = this.appMenuService.getAppMenus();
    
    this.menuItems = menus
      .filter((menu: any) => !menu.isTitle && menu.url)
      .map((menu: any) => ({
        title: menu.title || '',
        url: menu.url || '/',
        icon: this.mapIconToIonic(menu.icon)
      }));
  }

  private setupTabItems(): void {
    // Tabs principales para acceso rápido
    this.tabItems = [
      { title: 'Inicio', url: '/', icon: 'home-outline' },
      { title: 'Cuentas', url: '/accounting', icon: 'wallet-outline' },
      { title: 'Reportes', url: '/reports', icon: 'stats-chart-outline' },
      { title: 'Perfil', url: '/profile', icon: 'person-outline' }
    ];
  }

  private mapIconToIonic(colorAdminIcon: string): string {
    // Mapear íconos de FontAwesome a Ionicons
    const iconMap: { [key: string]: string } = {
      'fa fa-home': 'home-outline',
      'fa fa-user': 'person-outline',
      'fa fa-cog': 'settings-outline',
      'fa fa-wallet': 'wallet-outline',
      'fa fa-chart-line': 'stats-chart-outline',
      'fa fa-file': 'document-text-outline',
      'fa fa-building': 'business-outline',
      'fas fa-home': 'home-outline',
      'fas fa-user': 'person-outline',
      'bi bi-house': 'home-outline',
      'bi bi-person': 'person-outline',
    };

    return iconMap[colorAdminIcon] || 'ellipse-outline';
  }

  logout(): void {
    // Implementar lógica de logout
    console.log('Logout clicked');
  }

  ngOnDestroy(): void {
    if (this.menuSubscription) {
      this.menuSubscription.unsubscribe();
    }
  }
}
