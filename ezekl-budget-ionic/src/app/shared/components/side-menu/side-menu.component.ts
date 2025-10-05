import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import {
  IonMenu,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonList,
  IonListHeader,
  IonItem,
  IonIcon,
  IonLabel,
  IonAvatar,
  IonButton,
  IonMenuButton,
  IonCard,
  IonCardContent,
  IonChip,
  AlertController,
  ToastController,
  MenuController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  person,
  mail,
  call,
  card,
  checkmarkCircle,
  time,
  refresh,
  logOut,
  home,
  settings,
  helpCircle,
  close,
  pulse,
} from 'ionicons/icons';
import { AuthService } from '../../../services/auth.service';
import { AuthUser, AuthState } from '../../../models/auth.models';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-side-menu',
  templateUrl: './side-menu.component.html',
  styleUrls: ['./side-menu.component.scss'],
  imports: [
    CommonModule,
    IonMenu,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonList,
    IonListHeader,
    IonItem,
    IonIcon,
    IonLabel,
    IonAvatar,
    IonButton,
    IonCard,
    IonCardContent,
    IonChip,
  ],
})
export class SideMenuComponent implements OnInit {
  authState$: Observable<AuthState>;
  currentUser: AuthUser | undefined;

  constructor(
    private authService: AuthService,
    private router: Router,
    private alertController: AlertController,
    private toastController: ToastController,
    private menuController: MenuController
  ) {
    // Registrar iconos
    addIcons({
      person,
      mail,
      call,
      card,
      checkmarkCircle,
      time,
      refresh,
      logOut,
      home,
      settings,
      helpCircle,
      close,
      pulse,
    });

    // Configurar observables de autenticación
    this.authState$ = this.authService.authState;
  }

  ngOnInit() {
    // Suscribirse al estado de autenticación
    this.authState$.subscribe((state) => {
      this.currentUser = state.user;
    });
  }

  /**
   * Obtener iniciales del usuario para el avatar
   */
  getUserInitials(user: AuthUser): string {
    if (!user?.nameLogin) return '?';

    const names = user.nameLogin.split(' ');
    if (names.length >= 2) {
      return names[0][0] + names[1][0];
    }
    return user.nameLogin[0] || '?';
  }

  /**
   * Formatear tiempo de expiración del token
   */
  formatTokenExpiry(expiresAt?: Date): string {
    if (!expiresAt) return 'Desconocido';

    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();

    if (diff <= 0) return 'Expirado';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  }

  /**
   * Navegar a una página y cerrar menú
   */
  async navigateTo(path: string) {
    await this.menuController.close('main-menu');
    this.router.navigate([path]);
  }

  /**
   * Extender sesión manualmente
   */
  async extendSession() {
    try {
      const refreshed = await this.authService.refreshToken();

      if (refreshed) {
        const toast = await this.toastController.create({
          message: '✅ Sesión extendida exitosamente',
          duration: 3000,
          color: 'success',
          position: 'bottom',
          icon: 'checkmark-circle'
        });
        await toast.present();
      } else {
        const toast = await this.toastController.create({
          message: '❌ Error extendiendo la sesión',
          duration: 3000,
          color: 'danger',
          position: 'bottom',
          icon: 'alert-circle'
        });
        await toast.present();
      }
    } catch (error) {
      // Error silencioso para evitar logs innecesarios
    }
  }

  /**
   * Confirmar y ejecutar logout
   */
  async confirmLogout() {
    await this.menuController.close('main-menu');

    const alert = await this.alertController.create({
      header: 'Cerrar Sesión',
      message: '¿Estás seguro de que deseas cerrar tu sesión?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
        },
        {
          text: 'Cerrar Sesión',
          role: 'confirm',
          handler: () => {
            this.logout();
          },
        },
      ],
    });

    await alert.present();
  }

  /**
   * Ejecutar logout
   */
  private async logout() {
    try {
      await this.authService.logout();

      const toast = await this.toastController.create({
        message: 'Sesión cerrada exitosamente',
        duration: 2000,
        color: 'success',
        position: 'bottom',
      });
      await toast.present();

      this.router.navigate(['/login'], { replaceUrl: true });
    } catch (error) {
      const toast = await this.toastController.create({
        message: 'Error cerrando sesión',
        duration: 3000,
        color: 'danger',
        position: 'bottom',
      });
      await toast.present();

      this.router.navigate(['/login'], { replaceUrl: true });
    }
  }

  /**
   * Cerrar el menú lateral
   */
  async closeMenu() {
    await this.menuController.close('main-menu');
  }
}
