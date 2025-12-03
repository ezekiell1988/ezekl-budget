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
import { takeUntil, take } from 'rxjs/operators';
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
  logoMicrosoft,
  informationCircle,
  linkOutline,
  closeCircle
} from 'ionicons/icons';
import { Preferences } from '@capacitor/preferences';
import { environment } from '../../environments/environment';

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
  associateForm: FormGroup;

  // Observables públicos para el template
  wizardState$: Observable<LoginWizardState>;

  // Referencias a enums para el template
  loginSteps = LoginStep;

  // Controles individuales para los 5 dígitos
  tokenControls: FormControl[] = [];

  // Datos temporales para asociación Microsoft
  microsoftAssociationData: any = null;
  currentStep = LoginStep.REQUEST_TOKEN;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private toastController: ToastController,
    private alertController: AlertController
  ) {
    // Registrar iconos
    addIcons({
      wallet,
      logoMicrosoft,
      personCircle,
      alertCircle,
      linkOutline,
      informationCircle,
      closeCircle,
      mail,
      person,
      clipboard,
      arrowBack,
      refresh,
      checkmarkCircle
    });

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

    // Formulario para asociar cuenta Microsoft
    this.associateForm = this.fb.group({
      codeLogin: [
        '',
        [
          Validators.required,
          Validators.minLength(1),
          Validators.maxLength(10),
        ],
      ],
    });

    // Suscribirse al estado del wizard
    this.wizardState$ = this.authService.wizardState;
  }

  ngOnInit() {
    console.log('🔄 LoginPage ngOnInit - Iniciando');

    // Verificar si hay parámetros de callback PRIMERO (antes de cualquier verificación de autenticación)
    this.route.queryParams.pipe(take(1)).subscribe(params => {
      const hasCallbackParams = params['token'] || params['microsoft_pending'] === 'true' || params['microsoft_error'];

      if (hasCallbackParams) {
        console.log('🎯 Parámetros de callback detectados - Procesando callback PRIMERO');
        // Procesar callback de Microsoft ANTES de verificar autenticación
        this.checkForMicrosoftCallback();
        return;
      }

      // Si NO hay parámetros de callback, verificar si ya está autenticado
      console.log('🔍 Sin parámetros de callback - Verificando autenticación previa');
      if (this.authService.isAuthenticated) {
        console.log('✅ Usuario ya autenticado - Redirigiendo a home');
        this.router.navigate(['/home']);
        return;
      }

      console.log('🏁 Usuario no autenticado - Mostrando página de login');
    });

    // Resetear wizard al entrar (solo si no hay callback)
    this.authService.resetWizard();

    // Suscribirse a cambios del wizard para sincronizar currentStep
    this.wizardState$
      .pipe(takeUntil(this.destroy$))
      .subscribe((wizardState) => {
        // Solo actualizar si no estamos en el step de asociación Microsoft
        if (this.currentStep !== LoginStep.ASSOCIATE_MICROSOFT && wizardState?.currentStep) {
          this.currentStep = wizardState.currentStep;
        }
      });

    // Suscribirse a cambios de autenticación
    this.authService.authState
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        if (state.isAuthenticated) {
          console.log('🎉 Cambio de estado detectado - Usuario autenticado');
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
   * Verifica si hay token de Microsoft o necesidad de asociación en los parámetros de URL
   */
  private async checkForMicrosoftCallback() {
    console.log('🔍 Verificando parámetros de URL usando Angular ActivatedRoute');

    // Usar take(1) para procesar los parámetros una sola vez y evitar loops
    this.route.queryParams.pipe(take(1)).subscribe(params => {
      const systemToken = params['token'] || null; // Token del sistema para login directo
      const microsoftSuccess = params['microsoft_success'] || null;
      const microsoftError = params['microsoft_error'] || null;
      const microsoftPending = params['microsoft_pending'] || null;
      const codeLoginMicrosoft = params['codeLoginMicrosoft'] || null;
      const displayName = params['displayName'] || null;
      const email = params['email'] || null;

      console.log('📋 Query parameters detectados:', {
        microsoftPending,
        codeLoginMicrosoft: codeLoginMicrosoft ? 'PRESENTE' : 'AUSENTE',
        displayName: displayName ? decodeURIComponent(displayName) : 'AUSENTE',
        email: email ? decodeURIComponent(email) : 'AUSENTE',
        systemToken: systemToken ? 'PRESENTE' : 'AUSENTE', // Token del sistema
        microsoftSuccess,
        microsoftError
      });

      // Log específico para debugging
      if (microsoftPending === 'true') {
        console.log('🎯 microsoft_pending=true detectado - Mostrando componente de asociación');
        console.log('📄 URL completa:', window.location.href);
      } else if (systemToken) {
        console.log('🔑 Token del sistema detectado - Procesando autenticación');
      } else {
        console.log('🏠 Sin parámetros especiales - Mostrando componente normal de login');
      }

      // Procesar los parámetros si están presentes
      if (systemToken || microsoftError || microsoftPending === 'true') {
        this.processCallbackParameters(systemToken, microsoftSuccess, microsoftError, microsoftPending, codeLoginMicrosoft, displayName, email);
      }
    });
  }

  /**
   * Procesa los parámetros del callback de Microsoft
   */
  private async processCallbackParameters(
    systemToken: string | null, // Token del sistema para login directo (usuario ya asociado)
    microsoftSuccess: string | null,
    microsoftError: string | null,
    microsoftPending: string | null,
    codeLoginMicrosoft: string | null,
    displayName: string | null,
    email: string | null
  ) {
    console.log('🔄 Iniciando procesamiento de callback de Microsoft');

    // Manejar errores de Microsoft
    if (microsoftError) {
      console.error('❌ Error de autenticación con Microsoft:', microsoftError);
      this.showErrorToast('Error en la autenticación con Microsoft');
      // Limpiar URL usando Angular router
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: {},
        replaceUrl: true
      });
      return;
    }

    // Manejar asociación pendiente de Microsoft
    if (microsoftPending === 'true' && codeLoginMicrosoft && displayName && email) {
      console.log('🔗 Asociación de Microsoft pendiente detectada');

      // Establecer datos de Microsoft (usar propiedades locales)
      this.microsoftAssociationData = {
        codeLoginMicrosoft: decodeURIComponent(codeLoginMicrosoft),
        displayName: decodeURIComponent(displayName),
        email: decodeURIComponent(email)
      };

      console.log('💾 Datos de Microsoft guardados:', this.microsoftAssociationData);

      // Cambiar al step de asociación - MANTENER query params
      this.currentStep = LoginStep.ASSOCIATE_MICROSOFT;

      return; // Salir temprano, no procesar como login exitoso
    }

    // Manejar token exitoso de Microsoft (usuario ya asociado)
    if (systemToken && microsoftSuccess === 'true') {
      console.log('🔑 Procesando token de sistema para usuario Microsoft asociado');
      console.log('🔍 Token recibido longitud:', systemToken.length);

      // Limpiar el token de formato bytes si es necesario
      let cleanToken = systemToken;
      if (cleanToken.startsWith("b'") && cleanToken.endsWith("'")) {
        cleanToken = cleanToken.slice(2, -1); // Remover b' y '
        console.log('🧹 Token limpiado de formato bytes');
      }

      try {
        // Usar el token para obtener información completa del usuario
        console.log('🔍 Verificando token con el servidor para obtener datos del usuario...');

        // Usar el método del servicio de autenticación
        await this.authService.verifyMicrosoftToken(cleanToken);

        console.log('✅ Token verificado exitosamente');
        console.log('🔐 Estado de autenticación:', this.authService.isAuthenticated);
        console.log('👤 Usuario actual:', this.authService.currentUser?.name);

        // Verificar que se autenticó correctamente
        if (this.authService.isAuthenticated) {
          console.log('✅ Usuario autenticado exitosamente vía Microsoft');

          // Mostrar mensaje de éxito
          await this.showSuccessToast('¡Autenticación con Microsoft exitosa!');

          // IMPORTANTE: Limpiar parámetros de URL y redirigir en una sola operación
          console.log('🚀 Redirigiendo a /home con replaceUrl');
          await this.router.navigate(['/home'], {
            replaceUrl: true,
            queryParams: {} // Limpiar query params
          });

          console.log('✅ Navegación completada');
        } else {
          console.error('❌ AuthService no detectó autenticación tras verificación');
          this.showErrorToast('Error procesando autenticación');
        }

      } catch (error) {
        console.error('💥 Error verificando token con servidor:', error);
        this.showErrorToast('Error validando autenticación con Microsoft');

        // Limpiar URL en caso de error
        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: {},
          replaceUrl: true
        });
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
   * Asociar cuenta Microsoft con cuenta existente
   */
  async associateMicrosoftAccount() {
    if (this.associateForm.valid) {
      try {
        const codeLogin = this.associateForm.value.codeLogin;

        if (!this.microsoftAssociationData) {
          this.showErrorToast('Error: Datos de Microsoft no encontrados');
          return;
        }

        console.log('🔗 Iniciando asociación de cuentas:', {
          codeLogin,
          codeLoginMicrosoft: this.microsoftAssociationData.codeLoginMicrosoft
        });

        // Mostrar loading mientras se procesa
        this.showInfoToast('Asociando cuentas...');

        // Llamar al endpoint de asociación
        console.log('📞 Llamando al API de asociación...');
        const response = await this.associateMicrosoft(codeLogin, this.microsoftAssociationData.codeLoginMicrosoft);
        console.log('📨 Respuesta del API:', response);

        if (response.success) {
          // **HACER EXACTAMENTE LO MISMO QUE EL LOGIN NORMAL**
          // Usar el AuthService para procesar la respuesta de asociación
          await this.authService.processLoginResponse(response);

          // Mostrar mensaje de éxito
          this.showSuccessToast('¡Autenticación exitosa!');

          // El AuthService ya actualizó el estado, el ngOnInit detectará el cambio
          console.log('✅ Asociación y login procesados por AuthService');
        }

      } catch (error: any) {
        console.error('❌ Error en asociación:', error);
        this.showErrorToast(error.message || 'Error asociando cuenta Microsoft');
      }
    }
  }

  /**
   * Llama al endpoint de asociación Microsoft
   */
  private async associateMicrosoft(codeLogin: string, codeLoginMicrosoft: string): Promise<any> {
    const url = `${environment.apiUrl}/api/auth/microsoft/associate`;

    const body = {
      codeLogin: codeLogin,
      codeLoginMicrosoft: codeLoginMicrosoft
    };

    console.log('🌐 URL del endpoint:', url);
    console.log('📦 Body de la request:', body);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      console.log('📡 Status de respuesta:', response.status);
      console.log('📡 Content-Type:', response.headers.get('Content-Type'));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Error del servidor:', errorData);
        throw new Error(errorData.detail || `Error HTTP ${response.status}`);
      }

      const responseData = await response.json();
      console.log('✅ Datos de respuesta exitosa:', responseData);
      return responseData;

    } catch (error) {
      console.error('🚨 Error en fetch:', error);
      throw error;
    }
  }  /**
   * Cancelar asociación de Microsoft
   */
  cancelMicrosoftAssociation() {
    this.microsoftAssociationData = null;
    this.currentStep = LoginStep.REQUEST_TOKEN;
    // Resetear el wizard para volver al estado inicial
    this.authService.resetWizard();
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
