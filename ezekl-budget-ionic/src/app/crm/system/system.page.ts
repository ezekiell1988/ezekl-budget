import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { firstValueFrom } from 'rxjs';
import {
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonButton,
  IonIcon,
  IonGrid,
  IonRefresher,
  IonRefresherContent,
  IonChip,
  IonSkeletonText
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  heartOutline,
  keyOutline,
  bugOutline,
  refreshOutline,
  checkmarkCircle,
  closeCircle,
  warningOutline,
  timeOutline,
  serverOutline,
  cloudOutline,
  helpCircleOutline
} from 'ionicons/icons';

import { CrmService } from '../../services/crm.service';
import {
  CRMHealthResponse,
  CRMTokenResponse,
  CRMDiagnoseResponse
} from '../../models/crm.models';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';

@Component({
  selector: 'app-system',
  templateUrl: './system.page.html',
  styleUrls: ['./system.page.scss'],
  imports: [
    CommonModule,
    AppHeaderComponent,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonButton,
    IonIcon,
    IonGrid,
    IonRefresher,
    IonRefresherContent,
    IonChip,
    IonSkeletonText
  ]
})
export class SystemPage implements OnInit {
  private crmService = inject(CrmService);

  // Estado de la página
  isLoading = false;
  healthData: CRMHealthResponse | null = null;
  tokenData: CRMTokenResponse | null = null;
  diagnoseData: CRMDiagnoseResponse | null = null;

  // Estado de cada sección
  healthError: string | null = null;
  tokenError: string | null = null;
  diagnoseError: string | null = null;

  constructor() {
    addIcons({
      'heart-outline': heartOutline,
      'key-outline': keyOutline,
      'bug-outline': bugOutline,
      'refresh-outline': refreshOutline,
      'checkmark-circle': checkmarkCircle,
      'close-circle': closeCircle,
      'warning-outline': warningOutline,
      'time-outline': timeOutline,
      'server-outline': serverOutline,
      'cloud-outline': cloudOutline,
      'help-circle-outline': helpCircleOutline
    });
  }

  ngOnInit() {
    this.loadAllData();
  }

  /**
   * Carga todos los datos del sistema
   */
  async loadAllData() {
    this.isLoading = true;

    // Cargar datos en paralelo
    await Promise.all([
      this.loadHealthCheck(),
      this.loadTokenInfo(),
      this.loadDiagnosis()
    ]);

    this.isLoading = false;
  }

  /**
   * Carga el health check
   */
  async loadHealthCheck() {
    try {
      this.healthError = null;
      this.healthData = await firstValueFrom(this.crmService.getHealthCheck());
    } catch (error: any) {
      console.error('❌ Error cargando health check:', error);
      this.healthError = error.message || 'Error al cargar health check';
      this.healthData = null;
    }
  }

  /**
   * Carga información del token
   */
  async loadTokenInfo() {
    try {
      this.tokenError = null;
      this.tokenData = await firstValueFrom(this.crmService.getTokenInfo());
    } catch (error: any) {
      console.error('❌ Error cargando token info:', error);
      this.tokenError = error.message || 'Error al cargar información del token';
      this.tokenData = null;
    }
  }

  /**
   * Carga el diagnóstico completo
   */
  async loadDiagnosis() {
    try {
      this.diagnoseError = null;
      this.diagnoseData = await firstValueFrom(this.crmService.getDiagnosis());
    } catch (error: any) {
      console.error('❌ Error cargando diagnóstico:', error);
      this.diagnoseError = error.message || 'Error al cargar diagnóstico';
      this.diagnoseData = null;
    }
  }

  /**
   * Pull to refresh
   */
  async onRefresh(event: any) {
    await this.loadAllData();
    event.target.complete();
  }

  /**
   * Limpiar caché del token
   */
  async clearCache() {
    try {
      this.isLoading = true;
      await firstValueFrom(this.crmService.clearTokenCache());

      // Recargar datos después de limpiar caché
      await this.loadAllData();

      alert('✅ Caché limpiado exitosamente');
    } catch (error: any) {
      console.error('❌ Error limpiando caché:', error);
      alert('❌ Error al limpiar caché: ' + error.message);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Formato de fecha desde timestamp
   */
  formatTimestamp(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * Obtiene el color para el estado
   */
  getStatusColor(status: string): string {
    const statusLower = status.toLowerCase();
    if (statusLower === 'ok' || statusLower === 'success') return 'success';
    if (statusLower === 'error' || statusLower === 'failed') return 'danger';
    if (statusLower === 'warning') return 'warning';
    return 'medium';
  }

  /**
   * Obtiene el ícono para el estado
   */
  getStatusIcon(status: string): string {
    const statusLower = status.toLowerCase();
    if (statusLower === 'ok' || statusLower === 'success') return 'checkmark-circle';
    if (statusLower === 'error' || statusLower === 'failed') return 'close-circle';
    if (statusLower === 'warning') return 'warning-outline';
    return 'help-circle-outline';
  }

  /**
   * Obtiene entries de un objeto para iterar en template
   */
  getObjectEntries(obj: any): [string, any][] {
    return Object.entries(obj || {});
  }
}
