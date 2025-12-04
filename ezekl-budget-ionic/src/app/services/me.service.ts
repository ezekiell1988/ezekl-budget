/**
 * Servicio de gestión de menú y navegación
 * Maneja los elementos del menú lateral de forma centralizada
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

export interface MenuItem {
  id: string;
  title: string;
  icon: string;
  route?: string;
  action?: () => void;
  enabled: boolean;
  color?: string;
  badge?: {
    text: string;
    color: string;
  };
  children?: MenuItem[];
}

export interface MenuSection {
  id: string;
  title: string;
  items: MenuItem[];
}

@Injectable({
  providedIn: 'root'
})
export class MeService {

  private menuSections$ = new BehaviorSubject<MenuSection[]>([]);
  private isMenuOpen$ = new BehaviorSubject<boolean>(false);

  constructor(
    private router: Router,
    private authService: AuthService
  ) {
    this.initializeMenu();
  }

  /**
   * Observable de las secciones del menú
   */
  get menuSections(): Observable<MenuSection[]> {
    return this.menuSections$.asObservable();
  }

  /**
   * Observable del estado del menú (abierto/cerrado)
   */
  get isMenuOpen(): Observable<boolean> {
    return this.isMenuOpen$.asObservable();
  }

  /**
   * Inicializa la estructura del menú
   */
  private initializeMenu(): void {
    const sections: MenuSection[] = [
      {
        id: 'navigation',
        title: 'Navegación',
        items: [
          {
            id: 'home',
            title: 'Dashboard',
            icon: 'home',
            route: '/home',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'crm',
            title: 'Dynamics 365 CRM',
            icon: 'people-outline',
            route: '/crm',
            enabled: true,
            color: 'primary',
            badge: {
              text: 'NEW',
              color: 'success'
            }
          },
          {
            id: 'accounting-accounts',
            title: 'Cuentas Contables',
            icon: 'book-outline',
            route: '/accounting-accounts',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'companies',
            title: 'Compañías',
            icon: 'business-outline',
            route: '/companies',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'demo-websocket',
            title: 'Demo WebSocket',
            icon: 'pulse',
            route: '/demo-websocket',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'demo-realtime',
            title: 'Chat Realtime AI',
            icon: 'chatbubbles',
            route: '/demo-realtime',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'demo-copilot',
            title: 'Chat Copilot Studio',
            icon: 'chatbubbles',
            route: '/demo-copilot',
            enabled: true,
            color: 'secondary',
            badge: {
              text: 'NEW',
              color: 'success'
            }
          },
          {
            id: 'exam-question',
            title: 'Exam Questions',
            icon: 'book-outline',
            route: '/exam-question',
            enabled: true,
            color: 'primary'
          },
          {
            id: 'exam-review',
            title: 'Repaso Preguntas',
            icon: 'bookmark-outline',
            route: '/exam-review',
            enabled: true,
            color: 'tertiary',
            badge: {
              text: 'NEW',
              color: 'success'
            }
          }
        ]
      },
      {
        id: 'management',
        title: 'Gestión',
        items: [
          {
            id: 'transactions',
            title: 'Transacciones',
            icon: 'swap-horizontal',
            route: '/transactions',
            enabled: false, // TODO: Implementar
            color: 'medium'
          },
          {
            id: 'reports',
            title: 'Reportes',
            icon: 'bar-chart',
            route: '/reports',
            enabled: false, // TODO: Implementar
            color: 'medium'
          },
          {
            id: 'budgets',
            title: 'Presupuestos',
            icon: 'calculator',
            route: '/budgets',
            enabled: false, // TODO: Implementar
            color: 'medium'
          }
        ]
      },
      {
        id: 'configuration',
        title: 'Configuración',
        items: [
          {
            id: 'settings',
            title: 'Configuración',
            icon: 'settings',
            route: '/settings',
            enabled: false, // TODO: Implementar
            color: 'medium'
          },
          {
            id: 'help',
            title: 'Ayuda',
            icon: 'help-circle',
            route: '/help',
            enabled: false, // TODO: Implementar
            color: 'medium'
          }
        ]
      },
      {
        id: 'session',
        title: 'Sesión',
        items: [
          {
            id: 'extend-session',
            title: 'Extender Sesión',
            icon: 'refresh',
            enabled: true,
            color: 'success',
            action: () => this.extendSession()
          },
          {
            id: 'logout',
            title: 'Cerrar Sesión',
            icon: 'log-out',
            enabled: true,
            color: 'danger',
            action: () => this.logout()
          }
        ]
      }
    ];

    this.menuSections$.next(sections);
  }

  /**
   * Navega a una ruta específica
   */
  async navigateTo(route: string): Promise<void> {
    await this.closeMenu();
    this.router.navigate([route]);
  }

  /**
   * Ejecuta una acción de menú
   */
  async executeAction(item: MenuItem): Promise<void> {
    if (item.route) {
      await this.navigateTo(item.route);
    } else if (item.action) {
      await this.closeMenu();
      item.action();
    }
  }

  /**
   * Abre el menú lateral
   */
  openMenu(): void {
    this.isMenuOpen$.next(true);
  }

  /**
   * Cierra el menú lateral
   */
  async closeMenu(): Promise<void> {
    this.isMenuOpen$.next(false);
    // Pequeño delay para la animación
    return new Promise(resolve => setTimeout(resolve, 100));
  }

  /**
   * Alterna el estado del menú
   */
  toggleMenu(): void {
    const currentState = this.isMenuOpen$.value;
    if (currentState) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  /**
   * Obtiene un elemento específico del menú por ID
   */
  getMenuItem(id: string): MenuItem | undefined {
    const sections = this.menuSections$.value;

    for (const section of sections) {
      const item = section.items.find(item => item.id === id);
      if (item) {
        return item;
      }
    }

    return undefined;
  }

  /**
   * Actualiza un elemento del menú
   */
  updateMenuItem(id: string, updates: Partial<MenuItem>): void {
    const sections = this.menuSections$.value;

    for (const section of sections) {
      const itemIndex = section.items.findIndex(item => item.id === id);
      if (itemIndex !== -1) {
        section.items[itemIndex] = { ...section.items[itemIndex], ...updates };
        this.menuSections$.next([...sections]);
        return;
      }
    }
  }

  /**
   * Habilita un elemento del menú
   */
  enableMenuItem(id: string): void {
    this.updateMenuItem(id, { enabled: true, color: 'primary' });
  }

  /**
   * Deshabilita un elemento del menú
   */
  disableMenuItem(id: string): void {
    this.updateMenuItem(id, { enabled: false, color: 'medium' });
  }

  /**
   * Agrega un badge a un elemento del menú
   */
  setBadge(id: string, badge: { text: string; color: string }): void {
    this.updateMenuItem(id, { badge });
  }

  /**
   * Remueve el badge de un elemento del menú
   */
  removeBadge(id: string): void {
    this.updateMenuItem(id, { badge: undefined });
  }

  /**
   * Extiende la sesión del usuario
   */
  private async extendSession(): Promise<void> {
    try {
      const refreshed = await this.authService.refreshToken();

      if (refreshed) {
        // Mostrar notificación de éxito (será manejado por el componente)
        console.log('Sesión extendida exitosamente');
      } else {
        console.error('Error extendiendo la sesión');
      }
    } catch (error) {
      console.error('Error extendiendo sesión:', error);
    }
  }

  /**
   * Cierra la sesión del usuario con opciones
   */
  private async logout(): Promise<void> {
    // Importar AlertController dinámicamente para evitar dependencias circulares
    const { AlertController } = await import('@ionic/angular/standalone');
    const alertController = new AlertController();

    const alert = await alertController.create({
      header: 'Cerrar Sesión',
      message: '¿Cómo deseas cerrar tu sesión?',
      cssClass: 'logout-alert',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'alert-button-cancel',
        },
        {
          text: 'Solo esta aplicación',
          cssClass: 'alert-button-local',
          handler: async () => {
            await this.performLogout(false);
          },
        },
        {
          text: 'Cerrar sesión completa (Microsoft)',
          cssClass: 'alert-button-microsoft',
          handler: async () => {
            await this.performLogout(true);
          },
        },
      ],
    });

    await alert.present();
  }

  /**
   * Ejecuta el logout
   */
  private async performLogout(includeMicrosoft: boolean): Promise<void> {
    try {
      await this.authService.logout(includeMicrosoft);

      // Solo navegar si no hay redirección a Microsoft
      if (!includeMicrosoft) {
        this.router.navigate(['/login'], { replaceUrl: true });
      }
    } catch (error) {
      console.error('Error cerrando sesión:', error);
      // Forzar navegación a login incluso si hay error
      this.router.navigate(['/login'], { replaceUrl: true });
    }
  }

  /**
   * Obtiene estadísticas del menú
   */
  getMenuStats(): { total: number; enabled: number; disabled: number } {
    const sections = this.menuSections$.value;
    let total = 0;
    let enabled = 0;
    let disabled = 0;

    for (const section of sections) {
      for (const item of section.items) {
        total++;
        if (item.enabled) {
          enabled++;
        } else {
          disabled++;
        }
      }
    }

    return { total, enabled, disabled };
  }

  /**
   * Reinicia el menú a su estado inicial
   */
  resetMenu(): void {
    this.initializeMenu();
  }
}
