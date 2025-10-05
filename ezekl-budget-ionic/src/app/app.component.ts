import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { IonApp, IonRouterOutlet, ToastController } from '@ionic/angular/standalone';
import { AuthService } from './services/auth.service';
import { SideMenuComponent } from './shared/components/side-menu/side-menu.component';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  imports: [IonApp, IonRouterOutlet, SideMenuComponent],
})
export class AppComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private refreshIntervalId: any;

  constructor(
    private authService: AuthService,
    private toastController: ToastController
  ) {}

  ngOnInit() {
    // Iniciar timer de renovación automática de tokens
    this.startTokenRefreshTimer();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();

    // Limpiar interval
    if (this.refreshIntervalId) {
      clearInterval(this.refreshIntervalId);
    }
  }

  /**
   * Iniciar timer para verificar y renovar token automáticamente
   */
  private startTokenRefreshTimer(): void {
    // Verificar cada 5 minutos si el token necesita renovación
    this.refreshIntervalId = setInterval(async () => {
      if (this.authService.shouldRefreshToken()) {
        const refreshed = await this.authService.refreshToken();

        if (refreshed) {
          this.showTokenRefreshMessage('🔄 Sesión extendida automáticamente');
        } else {
          // El logout automático ya se maneja en refreshToken()
        }
      }
    }, 5 * 60 * 1000); // 5 minutos
  }

  /**
   * Mostrar mensaje de renovación de token al usuario
   */
  private async showTokenRefreshMessage(message: string): Promise<void> {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color: 'success',
      position: 'bottom',
      icon: 'checkmark-circle'
    });
    await toast.present();
  }

  /**
   * Método público para renovación manual de token (puede ser llamado desde cualquier página)
   */
  public async refreshTokenManually(): Promise<boolean> {
    const refreshed = await this.authService.refreshToken();

    if (refreshed) {
      this.showTokenRefreshMessage('✅ Sesión extendida manualmente');
      return true;
    } else {
      const errorToast = await this.toastController.create({
        message: '❌ Error extendiendo la sesión',
        duration: 3000,
        color: 'danger',
        position: 'bottom',
        icon: 'alert-circle'
      });
      await errorToast.present();
      return false;
    }
  }
}
