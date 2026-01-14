import { Component, OnInit, OnDestroy, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AppSettings, AuthService } from '../../service';
import { ResponsiveComponent } from '../../shared';
import { HeaderComponent, FooterComponent } from '../../components';
import {
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonSpinner,
  IonText,
  IonIcon,
  IonCardSubtitle
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { lockClosedOutline, mailOutline, arrowBackOutline, refreshOutline } from 'ionicons/icons';

@Component({
  selector: 'login-page',
  templateUrl: './login.html',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HeaderComponent,
    FooterComponent,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
    IonSpinner,
    IonText,
    IonIcon
  ]
})
export class LoginPage extends ResponsiveComponent implements OnInit, OnDestroy {
  // Paso 1: Solicitar PIN
  codeLogin: string = '';
  
  // Paso 2: Ingresar PIN
  idLogin: number | null = null;
  token: string = '';
  
  // Estados
  step: 'request' | 'verify' = 'request';
  loading: boolean = false;
  errorMessage: string = '';
  successMessage: string = '';
  
  // Timer para reenvío
  resendTimer: number = 0;
  private timerInterval: any;
  private returnUrl: string = '/home';

  // bg img
  public bgImageUrl: string = 'assets/img/login-bg.png?v=' + this.appSettings.apiVersion;

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    public appSettings: AppSettings,
    private renderer: Renderer2,
  ) {
    super();
    // Registrar íconos de Ionic
    addIcons({
      lockClosedOutline,
      mailOutline,
      arrowBackOutline,
      refreshOutline
    });
    // Inicializar estado de la aplicación si es necesario
    this.appSettings.appEmpty = true;
    this.renderer.addClass(document.body, 'bg-white');
  }

  // Retorna el título de la página para el header móvil
  getPageTitle(): string {
    return 'Iniciar Sesión';
  }

  ngOnInit() {
    // Leer returnUrl de los query params
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/home';
    
    // Verificar si ya está autenticado
    const isAuth = this.authService.isAuthenticated();
    
    if (isAuth) {
      this.router.navigate([this.returnUrl]);
    }
  }

  override ngOnDestroy() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }

    this.appSettings.appEmpty = false;
    this.renderer.removeClass(document.body, 'bg-white');
  }

  /**
   * Paso 1: Solicitar PIN (envía SMS y Email)
   */
  async requestPin() {
    if (!this.codeLogin || this.codeLogin.trim() === '') {
      this.errorMessage = 'Por favor ingrese su código de usuario';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.authService.requestLoginToken(this.codeLogin.trim()).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.idLogin = response.idLogin;
          this.step = 'verify';
          this.successMessage = 'Se ha enviado un PIN de 5 dígitos a tu teléfono y correo electrónico';
          this.startResendTimer();
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error solicitando PIN:', error);
        
        if (error.status === 404) {
          this.errorMessage = 'Usuario no encontrado. Verifica tu código de login';
        } else if (error.error?.detail) {
          this.errorMessage = error.error.detail;
        } else {
          this.errorMessage = 'Error al solicitar PIN. Intenta nuevamente';
        }
      }
    });
  }

  /**
   * Paso 2: Verificar PIN e iniciar sesión
   */
  async verifyPin() {
    if (!this.token || this.token.trim() === '') {
      this.errorMessage = 'Por favor ingrese el PIN de 5 dígitos';
      return;
    }

    if (this.token.length !== 5) {
      this.errorMessage = 'El PIN debe tener exactamente 5 dígitos';
      return;
    }

    if (!this.idLogin) {
      this.errorMessage = 'Error: ID de login no disponible';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.loginWithToken(this.idLogin, this.token.trim()).subscribe({
      next: async (response) => {
        this.loading = false;
        if (response.success) {
          console.log('✅ Login exitoso, token guardado');
          console.log('📱 Token:', response.token.substring(0, 20) + '...');
          console.log('👤 Usuario:', response.user);
          
          // Pequeño delay para asegurar que localStorage se sincronice en mobile
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // Verificar que el token se guardó correctamente
          const savedToken = this.authService.getToken();
          console.log('🔍 Token guardado verificado:', savedToken ? 'SÍ' : 'NO');
          
          if (!savedToken) {
            console.error('❌ Token no se guardó correctamente');
            this.errorMessage = 'Error guardando sesión. Intenta nuevamente';
            return;
          }
          
          // Redirigir a returnUrl o home
          console.log('🔄 Navegando a:', this.returnUrl);
          this.router.navigate([this.returnUrl]);
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error verificando PIN:', error);
        
        if (error.status === 401) {
          this.errorMessage = 'PIN inválido o expirado. Solicita uno nuevo';
        } else if (error.error?.detail) {
          this.errorMessage = error.error.detail;
        } else {
          this.errorMessage = 'Error al verificar PIN. Intenta nuevamente';
        }
      }
    });
  }

  /**
   * Volver al paso 1
   */
  backToRequest() {
    this.step = 'request';
    this.token = '';
    this.idLogin = null;
    this.errorMessage = '';
    this.successMessage = '';
    this.stopResendTimer();
  }

  /**
   * Reenviar PIN
   */
  resendPin() {
    if (this.resendTimer > 0) {
      return;
    }
    
    this.token = '';
    this.errorMessage = '';
    this.requestPin();
  }

  /**
   * Iniciar timer de 60 segundos para reenvío
   */
  private startResendTimer() {
    this.resendTimer = 60;
    this.timerInterval = setInterval(() => {
      this.resendTimer--;
      if (this.resendTimer <= 0) {
        this.stopResendTimer();
      }
    }, 1000);
  }

  /**
   * Detener timer de reenvío
   */
  private stopResendTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
    this.resendTimer = 0;
  }

  /**
   * Formatear entrada de PIN (solo números)
   */
  onPinInput(event: any) {
    const value = event.target.value;
    this.token = value.replace(/[^0-9]/g, '').substring(0, 5);
  }
}
