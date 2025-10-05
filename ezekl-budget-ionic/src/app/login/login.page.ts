import {
  Component,
  OnInit,
  OnDestroy,
  ViewChildren,
  QueryList,
  ElementRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from '@angular/forms';
import { Router } from '@angular/router';
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
  @ViewChildren('tokenInput', { read: ElementRef })
  tokenInputs!: QueryList<ElementRef>;

  private destroy$ = new Subject<void>();

  // Formularios reactivos
  step1Form: FormGroup;
  step2Form: FormGroup;

  // Observables públicos para el template
  wizardState$: Observable<LoginWizardState>;

  // Referencias a enums para el template
  loginSteps = LoginStep;

  // Controles del token para iteración en template
  tokenControls: FormControl[] = [];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private toastController: ToastController,
    private alertController: AlertController
  ) {
    // Registrar iconos
    addIcons({
      wallet,
      personCircle,
      person,
      mail,
      alertCircle,
      clipboard,
      arrowBack,
      refresh,
      'checkmark-circle': checkmarkCircle,
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

    // Crear controles para token de 5 dígitos
    this.tokenControls = Array.from(
      { length: 5 },
      () =>
        new FormControl('', [Validators.required, Validators.pattern(/^\d$/)])
    );

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

    // Quitar focus específicamente de los inputs del token si existen
    if (this.tokenInputs) {
      this.tokenInputs.forEach(input => {
        const nativeElement = input.nativeElement.querySelector('input');
        if (nativeElement && nativeElement.blur) {
          nativeElement.blur();
        }
      });
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
        const token = this.tokenControls
          .map((control) => control.value)
          .join('');
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
        // Llenar los inputs con el token
        for (let i = 0; i < 5; i++) {
          this.tokenControls[i].setValue(token[i]);
        }

        this.showSuccessToast('Token copiado automáticamente');

        // Auto-focus al último input y actualizar la UI
        setTimeout(() => {
          const inputs = this.tokenInputs.toArray();
          if (inputs[4]) {
            const lastInput = inputs[4].nativeElement;
            if (lastInput.setFocus) {
              lastInput.setFocus();
            } else {
              lastInput.focus();
            }
          }

          // Actualizar los valores visualmente
          inputs.forEach((input, i) => {
            if (input.nativeElement.value !== token[i]) {
              input.nativeElement.value = token[i];
            }
          });

          // Auto-submit si el formulario es válido
          if (this.step2Form.valid) {
            setTimeout(() => this.login(), 500);
          }
        }, 100);
      } else {
        this.showInfoToast('No se encontró un token válido en el portapapeles');
      }
    } catch (error) {
      this.showErrorToast('No se pudo acceder al portapapeles');
    }
  }

  /**
   * Manejo de input de dígitos del token
   */
  onTokenDigitInput(index: number, event: any, inputElement: any) {
    let value = event.detail?.value || event.target?.value || '';

    // Limpiar el valor si no es un dígito
    if (!/^\d$/.test(value)) {
      this.tokenControls[index].setValue('');
      inputElement.value = '';
      return;
    }

    // Establecer el valor en el control
    this.tokenControls[index].setValue(value);

    // Auto-focus al siguiente input si hay valor y no es el último
    if (value && index < 4) {
      setTimeout(() => {
        const inputs = this.tokenInputs.toArray();
        if (inputs[index + 1]) {
          const nextInput = inputs[index + 1].nativeElement;
          if (nextInput.setFocus) {
            nextInput.setFocus();
          } else {
            nextInput.focus();
          }
        }
      }, 50);
    }

    // Auto-submit cuando se complete el token
    if (index === 4 && value) {
      setTimeout(() => {
        if (this.step2Form.valid) {
          this.login();
        }
      }, 200);
    }
  }

  /**
   * Manejo de teclas en inputs de token
   */
  onTokenKeydown(index: number, event: KeyboardEvent) {
    const inputs = this.tokenInputs.toArray();

    // Backspace - ir al input anterior
    if (event.key === 'Backspace') {
      const currentValue = this.tokenControls[index].value;
      if (!currentValue && index > 0) {
        event.preventDefault();
        setTimeout(() => {
          if (inputs[index - 1]) {
            const prevInput = inputs[index - 1].nativeElement;
            if (prevInput.setFocus) {
              prevInput.setFocus();
            } else {
              prevInput.focus();
            }
            this.tokenControls[index - 1].setValue('');
          }
        }, 50);
      }
    }

    // Arrow keys para navegación
    if (event.key === 'ArrowLeft' && index > 0) {
      event.preventDefault();
      const prevInput = inputs[index - 1].nativeElement;
      if (prevInput.setFocus) {
        prevInput.setFocus();
      } else {
        prevInput.focus();
      }
    }

    if (event.key === 'ArrowRight' && index < 4) {
      event.preventDefault();
      const nextInput = inputs[index + 1].nativeElement;
      if (nextInput.setFocus) {
        nextInput.setFocus();
      } else {
        nextInput.focus();
      }
    }

    // Prevenir entrada de caracteres no numéricos
    if (!/\d|Backspace|ArrowLeft|ArrowRight|Tab/.test(event.key)) {
      event.preventDefault();
    }
  }

  /**
   * Click en input de token
   */
  onTokenInputClick(index: number) {
    // Si hay inputs vacíos anteriores, ir al primero vacío
    for (let i = 0; i < index; i++) {
      if (!this.tokenControls[i].value) {
        const inputs = this.tokenInputs.toArray();
        if (inputs[i]) {
          inputs[i].nativeElement.focus();
        }
        return;
      }
    }
  }

  /**
   * Limpiar inputs de token
   */
  clearTokenInputs() {
    this.tokenControls.forEach((control) => control.setValue(''));

    // Limpiar también los valores visibles de los inputs
    setTimeout(() => {
      const inputs = this.tokenInputs.toArray();
      inputs.forEach((input) => {
        if (input.nativeElement.value) {
          input.nativeElement.value = '';
        }
      });

      // Focus al primer input
      if (inputs[0]) {
        const firstInput = inputs[0].nativeElement;
        if (firstInput.setFocus) {
          firstInput.setFocus();
        } else {
          firstInput.focus();
        }
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
