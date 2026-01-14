import { Component, OnInit, OnDestroy, Renderer2, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AppSettings, AuthService, LoggerService } from '../../service';
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
  // Logger con contexto
  private readonly logger = inject(LoggerService).getLogger('LoginPage');
  
  // Paso 1: Solicitar PIN
  codeLogin: string = '';
  
  // Paso 2: Ingresar PIN (ya no necesitamos idLogin)
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
   * Paso 1: Solicitar PIN (envía Email)
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
        if (response.success && response.tokenGenerated) {
          this.step = 'verify';
          this.successMessage = 'Se ha enviado un PIN de 5 dígitos a tu correo electrónico';
          this.startResendTimer();
          this.logger.success('PIN enviado correctamente al email');
        } else {
          this.errorMessage = response.message || 'Error al generar token';
          this.logger.warn('Error al generar token:', response.message);
        }
      },
      error: (error) => {
        this.loading = false;
        this.logger.error('Error solicitando PIN:', error);
        
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

    if (!this.codeLogin) {
      this.errorMessage = 'Error: código de login no disponible';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.loginWithToken(this.codeLogin.trim(), this.token.trim()).subscribe({
      next: async (response) => {
        this.loading = false;
        if (response.success && response.accessToken) {
          this.logger.success('Login exitoso, token guardado');
          this.logger.debug('Token recibido:', response.accessToken.substring(0, 20) + '...');
          this.logger.debug('Usuario autenticado:', response.user.nameLogin);
          
          // Pequeño delay para asegurar que localStorage se sincronice en mobile
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // Verificar que el token se guardó correctamente
          const savedToken = this.authService.getToken();
          this.logger.debug('Token guardado verificado:', savedToken ? 'SÍ' : 'NO');
          
          if (!savedToken) {
            this.logger.error('Token no se guardó correctamente en localStorage');
            this.errorMessage = 'Error guardando sesión. Intenta nuevamente';
            return;
          }
          
          // Redirigir a returnUrl o home
          this.logger.info('Navegando a:', this.returnUrl);
          this.router.navigate([this.returnUrl]);
        } else {
          this.errorMessage = response.message || 'Error en la autenticación';
          this.logger.warn('Error en autenticación:', response.message);
        }
      },
      error: (error) => {
        this.loading = false;
        this.logger.error('Error verificando PIN:', error);
        
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
