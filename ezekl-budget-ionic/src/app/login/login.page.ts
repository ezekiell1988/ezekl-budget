import {
  Component,
  OnInit,
  OnDestroy,
  ViewChildren,
  QueryList,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Subject, Observable } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import {
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
  IonIcon,
  IonSpinner,
  IonAvatar,
  IonGrid,
  IonRow,
  IonCol,
  IonText,
  IonNote,
  IonChip,
  ToastController,
  AlertController,
  ViewWillLeave,
  ViewDidLeave,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  wallet,
  personCircle,
  person,
  mail,
  alertCircle,
  clipboard,
  arrowBack,
  refresh,
  checkmarkCircle,
  logoMicrosoft
} from 'ionicons/icons';

import { AuthService } from '../services/auth.service';
import {
  RequestTokenResponse,
  LoginResponse,
  LoginStep,
  LoginWizardState,
} from '../models/auth.models';


@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
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
    IonIcon,
    IonSpinner,
    IonAvatar,
    IonGrid,
    IonRow,
    IonCol,
    IonText,
    IonNote,
    IonChip,
  ],
})
export class LoginPage implements OnInit, OnDestroy, ViewWillLeave, ViewDidLeave {
  @ViewChildren('tokenInput') tokenInputs!: QueryList<any>;

  private destroy$ = new Subject<void>();

  // Formularios reactivos
  step1Form: FormGroup;
  step2Form: FormGroup;

  // Observables públicos para el template
  wizardState$: Observable<LoginWizardState>;

  // Referencias a enums para el template
  loginSteps = LoginStep;

  // Controles individuales para los 5 dígitos
  tokenControls: FormControl[] = [];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private toastController: ToastController,
    private alertController: AlertController
  ) {
    // Registrar iconos
    addIcons({wallet,logoMicrosoft,personCircle,alertCircle,mail,person,clipboard,arrowBack,refresh,'checkmarkCircle':checkmarkCircle,});

    // Inicializar formularios
    this.step1Form = this.fb.group({
      codeLogin: [
        '',
        [
          Validators.required,
          Validators.minLength(1),
          Validators.maxLength(10),
        ],
      ],
    });

    // Crear 5 controles individuales para el token
    this.tokenControls = Array.from(
      { length: 5 },
      () => new FormControl('', [Validators.required, Validators.pattern(/^\d$/)])
    );

    // Formulario con los 5 dígitos individuales
    this.step2Form = this.fb.group({
      digit1: this.tokenControls[0],
      digit2: this.tokenControls[1],
      digit3: this.tokenControls[2],
      digit4: this.tokenControls[3],
      digit5: this.tokenControls[4],
    });

    // Suscribirse al estado del wizard
    this.wizardState$ = this.authService.wizardState;
  }

  ngOnInit() {
    // Verificar si ya está autenticado
    if (this.authService.isAuthenticated) {
      this.router.navigate(['/home']);
      return;
    }

    // Verificar si hay token de Microsoft en los parámetros de URL (callback de Microsoft)
    this.checkForMicrosoftCallback();

    // Resetear wizard al entrar
    this.authService.resetWizard();

    // Suscribirse a cambios de autenticación
    this.authService.authState
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        if (state.isAuthenticated) {
          this.showSuccessToast('¡Bienvenido!');
          // Usar un pequeño delay para evitar conflictos con guards
          setTimeout(() => {
            this.router.navigate(['/home']);
          }, 100);
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Ionic lifecycle: Antes de salir de la vista
   * Quita el focus de cualquier elemento para evitar conflictos aria-hidden
   */
  ionViewWillLeave() {
    // Quitar focus de cualquier elemento activo
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement && activeElement.blur) {
      activeElement.blur();
    }
  }

  /**
   * Ionic lifecycle: Después de salir de la vista
   * Limpieza adicional si es necesaria
   */
  ionViewDidLeave() {
    // Limpieza adicional si es necesaria
  }

  /**
   * Verifica si hay token de Microsoft en los parámetros de URL
   */
  private async checkForMicrosoftCallback() {
    // Obtener parámetros de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const expires = urlParams.get('expires');

    if (token && expires) {
      try {
        // Simular respuesta de login exitoso para activar el flujo normal de autenticación
        const mockResponse: LoginResponse = {
          success: true,
          message: 'Autenticación con Microsoft exitosa',
          accessToken: token,
          expiresAt: expires,
          user: undefined // Se obtendrá del token
        };

        // Usar el método interno del AuthService para establecer la sesión
        // Por ahora, guardamos directamente en localStorage como lo hace el AuthService
        localStorage.setItem('ezekl_auth_token', token);
        localStorage.setItem('ezekl_auth_expires', expires);

        // Limpiar URL
        window.history.replaceState({}, document.title, window.location.pathname);

        // Mostrar mensaje de éxito y redirigir
        this.showSuccessToast('¡Autenticación con Microsoft exitosa!');

        // Forzar recarga para que el AuthService detecte el token
        setTimeout(() => {
          window.location.reload();
        }, 1500);

      } catch (error) {
        console.error('Error procesando autenticación de Microsoft:', error);
        this.showErrorToast('Error procesando autenticación de Microsoft');
        // Limpiar URL en caso de error
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }

  /**
   * Login con Microsoft
   */
  loginWithMicrosoft() {
    try {
      // Usar el servicio de autenticación para obtener la URL de Microsoft
      const microsoftUrl = this.authService.getMicrosoftAuthUrl();

      // Abrir en la misma ventana para manejar el callback correctamente
      window.location.href = microsoftUrl;

    } catch (error: any) {
      this.showErrorToast(error.message || 'Error iniciando sesión con Microsoft');
    }
  }

  /**
   * PASO 1: Solicitar token
   */
  async requestToken() {
    if (this.step1Form.valid) {
      try {
        const codeLogin = this.step1Form.value.codeLogin;
        const response = await this.authService.requestToken(codeLogin);

        if (response.success) {
          this.showSuccessToast('Token enviado a tu email');
          // El servicio automáticamente cambia al siguiente paso
        }
      } catch (error: any) {
        this.showErrorToast(error.message || 'Error solicitando token');
      }
    }
  }

  /**
   * PASO 2: Login con token
   */
  async login() {
    if (this.step2Form.valid) {
      try {
        const token = this.tokenControls.map(control => control.value).join('');
        const codeLogin = this.step1Form.value.codeLogin;

        const response = await this.authService.login(codeLogin, token);

        if (response.success) {
          // El servicio automáticamente actualiza el estado y el ngOnInit redirige
        }
      } catch (error: any) {
        this.showErrorToast(error.message || 'Error de autenticación');
        this.clearTokenInputs();
      }
    }
  }

  /**
   * Reenviar token
   */
  async resendToken() {
    try {
      await this.authService.resendToken();
      this.showSuccessToast('Token reenviado');
      this.clearTokenInputs();
    } catch (error: any) {
      this.showErrorToast(error.message || 'Error reenviando token');
    }
  }

  /**
   * Volver al paso anterior
   */
  goBack() {
    this.authService.goBackInWizard();
    this.clearTokenInputs();
  }

  /**
   * Intentar auto-copiar token desde portapapeles
   */
  async tryAutoCopy() {
    try {
      const token = await this.authService.tryAutoCopyToken();

      if (token && token.length === 5) {
        // Llenar cada input individualmente
        for (let i = 0; i < 5; i++) {
          this.tokenControls[i].setValue(token[i]);
        }

        this.showSuccessToast('Token copiado automáticamente');

        // Auto-submit si el formulario es válido
        setTimeout(() => {
          if (this.step2Form.valid) {
            this.login();
          }
        }, 500);
      } else {
        this.showInfoToast('No se encontró un token válido en el portapapeles');
      }
    } catch (error) {
      this.showErrorToast('No se pudo acceder al portapapeles');
    }
  }

  /**
   * Manejo de input para cada dígito
   */
  onDigitInput(index: number, event: any, inputElement: any) {
    let value = event.detail?.value || '';

    // Mantener solo el último dígito ingresado
    if (!/^\d$/.test(value)) {
      this.tokenControls[index].setValue('');
      return;
    }

    this.tokenControls[index].setValue(value);

    // Auto-focus al siguiente input
    if (value && index < 4) {
      setTimeout(() => {
        const inputs = this.tokenInputs.toArray();
        if (inputs[index + 1]) {
          inputs[index + 1].setFocus();
        }
      }, 50);
    }

    // Auto-submit cuando se complete el último dígito
    if (index === 4 && value && this.step2Form.valid) {
      setTimeout(() => {
        this.login();
      }, 300);
    }
  }

  /**
   * Manejo de teclas especiales
   */
  onDigitKeydown(index: number, event: KeyboardEvent) {
    // Backspace - ir al input anterior
    if (event.key === 'Backspace' && !this.tokenControls[index].value && index > 0) {
      event.preventDefault();
      const inputs = this.tokenInputs.toArray();
      if (inputs[index - 1]) {
        inputs[index - 1].setFocus();
        this.tokenControls[index - 1].setValue('');
      }
    }

    // Prevenir caracteres no numéricos
    if (!/\d|Backspace|ArrowLeft|ArrowRight|Tab/.test(event.key)) {
      event.preventDefault();
    }
  }

  /**
   * Focus en un dígito específico
   */
  onDigitFocus(index: number) {
    // Si hay inputs vacíos anteriores, ir al primero vacío
    for (let i = 0; i < index; i++) {
      if (!this.tokenControls[i].value) {
        const inputs = this.tokenInputs.toArray();
        if (inputs[i]) {
          inputs[i].setFocus();
        }
        return;
      }
    }
  }

  /**
   * Limpiar todos los inputs del token
   */
  clearTokenInputs() {
    this.tokenControls.forEach(control => control.setValue(''));

    // Focus al primer input
    setTimeout(() => {
      const inputs = this.tokenInputs.toArray();
      if (inputs[0]) {
        inputs[0].setFocus();
      }
    }, 100);
  }

  /**
   * TrackBy function para ngFor
   */
  trackByIndex(index: number): number {
    return index;
  }

  // ================================
  // Métodos de UI/UX
  // ================================

  private async showSuccessToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color: 'success',
      position: 'bottom',
      icon: 'checkmark-circle',
    });
    await toast.present();
  }

  private async showErrorToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 4000,
      color: 'danger',
      position: 'bottom',
      icon: 'alert-circle',
    });
    await toast.present();
  }

  private async showInfoToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color: 'primary',
      position: 'bottom',
      icon: 'information-circle',
    });
    await toast.present();
  }
}
