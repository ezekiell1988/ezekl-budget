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
  templateUrl: './mobile-layout.component.html',
  styleUrls: ['./mobile-layout.component.scss']
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
