import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { addIcons } from 'ionicons';
import { AppSettings, LoggerService } from '../../service';
import { HeaderComponent, FooterComponent } from '../../components';
import { 
  walletOutline, 
  trendingUpOutline, 
  trendingDownOutline,
  cashOutline,
  arrowForwardOutline
} from 'ionicons/icons';
import { 
  IonContent,
  IonCard, 
  IonCardHeader, 
  IonCardTitle, 
  IonCardContent,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonButton,
  IonBadge
} from '@ionic/angular/standalone';
import { ResponsiveComponent } from '../../shared';
import { PanelComponent } from '../../components';

@Component({
  selector: 'home',
  templateUrl: './home.html',
  standalone: true,
  imports: [
    CommonModule,
    HeaderComponent,
    FooterComponent,
    PanelComponent,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonList,
    IonItem,
    IonLabel,
    IonIcon,
    IonButton,
    IonBadge
  ]
})
export class HomePage extends ResponsiveComponent {
  // Datos de ejemplo (lógica compartida entre ambos layouts)
  accountSummary = {
    totalBalance: 15750.50,
    income: 5200.00,
    expenses: 3450.00,
    savings: 1750.00
  };

  recentTransactions = [
    { id: 1, description: 'Pago de servicios', amount: -150.00, date: new Date(), type: 'expense' },
    { id: 2, description: 'Depósito salario', amount: 2500.00, date: new Date(), type: 'income' },
    { id: 3, description: 'Compra supermercado', amount: -85.50, date: new Date(), type: 'expense' },
    { id: 4, description: 'Transferencia recibida', amount: 500.00, date: new Date(), type: 'income' },
  ];

  private readonly logger = inject(LoggerService).getLogger('HomePage');

  constructor(public appSettings: AppSettings) {
    super();
    // Registrar íconos de Ionic
    addIcons({
      walletOutline,
      trendingUpOutline,
      trendingDownOutline,
      cashOutline,
      arrowForwardOutline
    });
  }
  
  // Retorna el título de la página para el header móvil
  getPageTitle(): string {
    return 'Inicio';
  }
  
  // Métodos compartidos (misma lógica para ambos layouts)
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('es-CR', {
      style: 'currency',
      currency: 'CRC'
    }).format(amount);
  }

  getTransactionIcon(type: string): string {
    return type === 'income' ? 'trending-up-outline' : 'trending-down-outline';
  }

  getTransactionColor(type: string): string {
    return type === 'income' ? 'success' : 'danger';
  }

  // Método para pull-to-refresh (Ionic)
  handleRefresh(event: any): void {
    setTimeout(() => {
      // Aquí iría la lógica de actualización
      this.logger.debug('Datos actualizados');
      event.target.complete();
    }, 1500);
  }

  // Métodos de navegación
  viewAllTransactions(): void {
    this.logger.debug('Ver todas las transacciones');
    // Implementar navegación
  }

  addTransaction(): void {
    this.logger.debug('Agregar transacción');
    // Implementar lógica
  }
}
