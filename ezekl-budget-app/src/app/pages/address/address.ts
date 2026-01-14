/// <reference types="@types/google.maps" />

import {
  Component,
  OnInit,
  OnDestroy,
  AfterViewInit,
  ViewChild,
  ElementRef,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { addIcons } from 'ionicons';
import {
  locate,
  checkmark,
  add, chevronUpCircle } from 'ionicons/icons';
import {
  IonContent,
  IonButton,
  IonIcon,
  IonSpinner,
  IonSkeletonText,
  IonSearchbar,
  IonFab,
  IonFabButton,
  IonFabList,
  ToastController,
} from '@ionic/angular/standalone';
import { AppSettings, ClickeatService } from '../../service';
import { ResponsiveComponent } from '../../shared';
import { environment } from '../../../environments/environment';
import { CustomerAddressAddRequest, CustomerAddressAddResponse } from '../../shared/models';
import Swal from 'sweetalert2';

interface LatLng {
  lat: number;
  lng: number;
}

declare global {
  interface Window {
    google: typeof google;
  }
}

@Component({
  selector: 'address',
  templateUrl: './address.html',
  styleUrls: ['./address.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonButton,
    IonIcon,
    IonSpinner,
    IonSkeletonText,
    IonSearchbar,
    IonFab,
    IonFabButton,
    IonFabList,
  ],
})
export class AddressPage extends ResponsiveComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('mapContainer', { static: false }) mapContainer!: ElementRef;
  @ViewChild('searchbar', { static: false }) searchbar!: IonSearchbar;
  @ViewChild('searchInput', { static: false }) searchInput!: ElementRef<HTMLInputElement>;

  phone: string = '';
  map: google.maps.Map | null = null;
  marker: google.maps.marker.AdvancedMarkerElement | null = null;
  selectedLocation: LatLng | null = null;
  selectedAddress: string = '';
  isLoadingLocation: boolean = false;
  isMapReady: boolean = false;
  isSavingAddress: boolean = false;
  autocomplete: HTMLElement | null = null;
  autocompleteInput: HTMLInputElement | null = null;
  darkModeMediaQuery: MediaQueryList | null = null;
  
  private paramSubscription?: Subscription;
  private viewInitialized = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private clickeatService: ClickeatService,
    public appSettings: AppSettings,
    private toastController: ToastController
  ) {
    super();
    addIcons({locate,chevronUpCircle,checkmark,add});
    
    // Configurar layout para pantalla completa sin sidebar/header
    this.appSettings.appEmpty = true;
    this.appSettings.appContentFullHeight = true;
    this.appSettings.appContentClass = 'p-0 position-relative';
  }

  ngOnInit() {
    // Suscribirse a cambios en los parámetros de ruta
    this.paramSubscription = this.route.paramMap.subscribe(params => {
      const newPhone = params.get('phone') || '';
      
      // Si el teléfono cambió, actualizar
      if (this.phone !== newPhone) {
        this.phone = newPhone;
        
        // Si ya hay un autocomplete, limpiarlo completamente
        if (this.autocomplete) {
          // Remover el elemento del DOM
          this.autocomplete.remove();
          this.autocomplete = null;
          
          // Restaurar el input original si existe
          if (this.autocompleteInput) {
            this.autocompleteInput.style.display = '';
            this.autocompleteInput = null;
          }
          
          // Reinicializar después de que Angular actualice el DOM
          setTimeout(() => {
            this.initAutocomplete();
          }, 200);
        }
      }
      
      // Si la vista ya está inicializada y no hay mapa, cargar
      if (this.viewInitialized && !this.map && !this.isLoadingLocation) {
        this.loadGoogleMaps();
      }
    });
    
    this.setupThemeListener();
  }

  ngAfterViewInit() {
    // Marcar que la vista está lista
    this.viewInitialized = true;
    
    // Si ya tenemos teléfono y no hay mapa, cargar ahora
    if (this.phone && !this.map && !this.isLoadingLocation) {
      this.loadGoogleMaps();
    }
  }

  override ngOnDestroy() {
    // Limpiar suscripción
    if (this.paramSubscription) {
      this.paramSubscription.unsubscribe();
    }
    
    if (this.marker) {
      this.marker.map = null;
    }
    if (this.darkModeMediaQuery) {
      this.darkModeMediaQuery.removeEventListener(
        'change',
        this.handleThemeChange
      );
    }
    
    // Restaurar configuración de layout
    this.appSettings.appEmpty = false;
    this.appSettings.appContentFullHeight = false;
    this.appSettings.appContentClass = '';
  }

  getPageTitle(): string {
    return 'Seleccionar Dirección';
  }

  setupThemeListener() {
    this.darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    this.darkModeMediaQuery.addEventListener('change', this.handleThemeChange);
  }

  handleThemeChange = () => {
    if (this.map) {
      const prefersDark = window.matchMedia(
        '(prefers-color-scheme: dark)'
      ).matches;
      this.map.setOptions({
        styles: prefersDark ? this.getDarkModeStyles() : [],
      });
    }
  };

  getDarkModeStyles(): google.maps.MapTypeStyle[] {
    return [
      { elementType: 'geometry', stylers: [{ color: '#242f3e' }] },
      { elementType: 'labels.text.stroke', stylers: [{ color: '#242f3e' }] },
      { elementType: 'labels.text.fill', stylers: [{ color: '#746855' }] },
      {
        featureType: 'administrative.locality',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#d59563' }],
      },
      {
        featureType: 'poi',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#d59563' }],
      },
      {
        featureType: 'poi.park',
        elementType: 'geometry',
        stylers: [{ color: '#263c3f' }],
      },
      {
        featureType: 'poi.park',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#6b9a76' }],
      },
      {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [{ color: '#38414e' }],
      },
      {
        featureType: 'road',
        elementType: 'geometry.stroke',
        stylers: [{ color: '#212a37' }],
      },
      {
        featureType: 'road',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#9ca5b3' }],
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry',
        stylers: [{ color: '#746855' }],
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry.stroke',
        stylers: [{ color: '#1f2835' }],
      },
      {
        featureType: 'road.highway',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#f3d19c' }],
      },
      {
        featureType: 'transit',
        elementType: 'geometry',
        stylers: [{ color: '#2f3948' }],
      },
      {
        featureType: 'transit.station',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#d59563' }],
      },
      {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [{ color: '#17263c' }],
      },
      {
        featureType: 'water',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#515c6d' }],
      },
      {
        featureType: 'water',
        elementType: 'labels.text.stroke',
        stylers: [{ color: '#17263c' }],
      },
    ];
  }

  async loadGoogleMaps() {
    // Verificar si Google Maps ya está cargado
    if (typeof window !== 'undefined' && window.google && window.google.maps) {
      // Si ya existe el mapa, no reinicializarlo, solo actualizar si es necesario
      if (!this.map) {
        await this.initMap();
      }
      return;
    }

    // Verificar si ya se está cargando
    if ((window as any).googleMapsLoading) {
      // Esperar a que termine de cargar
      const checkInterval = setInterval(() => {
        if ((window as any).googleMapsLoaded && !this.map) {
          clearInterval(checkInterval);
          this.initMap();
        }
      }, 100);
      return;
    }

    try {
      // Marcar como cargando
      (window as any).googleMapsLoading = true;

      // Obtener API key desde el backend
      const response = await fetch(`${environment.apiUrl}system/google-map-api-key.json`);
      const data = await response.json();

      if (!data.success || !data.apiKey) {
        throw new Error(data.error || 'No se pudo obtener la API key');
      }

      // Cargar script de Google Maps con loading=async para mejor rendimiento
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${data.apiKey}&libraries=places,geometry,marker&loading=async&callback=initGoogleMaps`;
      script.async = true;
      script.defer = true;
      script.id = 'google-maps-script';

      // Definir callback global para cuando Google Maps esté listo
      (window as any).initGoogleMaps = () => {
        (window as any).googleMapsLoading = false;
        (window as any).googleMapsLoaded = true;
        this.initMap();
      };

      script.onerror = () => {
        (window as any).googleMapsLoading = false;
        this.isLoadingLocation = false;
      };

      document.head.appendChild(script);
    } catch (error) {
      (window as any).googleMapsLoading = false;
      this.isLoadingLocation = false;
    }
  }

  async initMap() {
    // Obtener ubicación actual
    this.isLoadingLocation = true;
    try {
      const position = await this.getCurrentPosition();
      const currentLocation: LatLng = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      this.selectedLocation = currentLocation;
      this.cdr.detectChanges();
      this.createMap(currentLocation);
    } catch (error) {
      // Ubicación por defecto (San José, Costa Rica)
      const defaultLocation: LatLng = { lat: 9.9281, lng: -84.0907 };
      this.selectedLocation = defaultLocation;
      this.cdr.detectChanges();
      this.createMap(defaultLocation);
    } finally {
      this.isLoadingLocation = false;
    }
  }

  createMap(location: LatLng) {
    if (!this.mapContainer) {
      setTimeout(() => this.createMap(location), 100);
      return;
    }
    
    const mapOptions: google.maps.MapOptions = {
      center: location,
      zoom: 15,
      mapId: 'CLICKEAT_MAP', // ID requerido para AdvancedMarkerElement
      disableDefaultUI: false,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    };

    this.map = new google.maps.Map(this.mapContainer.nativeElement, mapOptions);

    // Crear marcador fijo en el centro usando AdvancedMarkerElement
    this.marker = new google.maps.marker.AdvancedMarkerElement({
      position: location,
      map: this.map,
    });

    this.selectedLocation = location;

    // Evento cuando se mueve el mapa (center_changed se dispara continuamente mientras se arrastra)
    this.map.addListener('center_changed', () => {
      const center = this.map?.getCenter();
      if (center && this.marker) {
        // AdvancedMarkerElement usa propiedad 'position' directamente
        this.marker.position = center;
      }
    });

    // Evento cuando termina de moverse el mapa (para actualizar selectedLocation)
    this.map.addListener('idle', () => {
      const center = this.map?.getCenter();
      if (center) {
        this.selectedLocation = {
          lat: center.lat(),
          lng: center.lng(),
        };
        // Limpiar dirección si se movió el mapa manualmente
        this.selectedAddress = '';
        this.cdr.detectChanges();
      }
    });

    this.isMapReady = true;
    this.cdr.detectChanges();
    
    // Forzar actualización después de un pequeño delay para asegurar renderizado
    setTimeout(() => {
      this.cdr.detectChanges();
      
      // Inicializar Places Autocomplete después de asegurar que el DOM está actualizado
      setTimeout(() => {
        this.initAutocomplete();
      }, 200);
    }, 50);
  }

  async initAutocomplete() {
    // Para versión móvil usa ion-searchbar
    if (this.isMobile()) {
      if (!this.searchbar) {
        setTimeout(() => this.initAutocomplete(), 150);
        return;
      }
      
      try {
        const input = await this.searchbar.getInputElement();
        if (!input) {
          setTimeout(() => this.initAutocomplete(), 150);
          return;
        }
        this.setupAutocomplete(input);
      } catch (error) {
        setTimeout(() => this.initAutocomplete(), 150);
      }
    }
    // Para versión desktop usa input normal
    else if (this.isDesktop()) {
      if (!this.searchInput?.nativeElement) {
        setTimeout(() => this.initAutocomplete(), 150);
        return;
      }
      this.setupAutocomplete(this.searchInput.nativeElement);
    }
  }

  setupAutocomplete(input: HTMLInputElement) {
    // Verificar si ya existe un autocomplete para evitar duplicados
    if (this.autocomplete) {
      return;
    }
    
    // Guardar referencia al input original
    this.autocompleteInput = input;
    
    // Crear PlaceAutocompleteElement (recomendado por Google)
    const autocompleteElement = document.createElement('gmp-place-autocomplete') as any;
    
    // Configurar para Costa Rica
    autocompleteElement.setAttribute('country', 'cr');
    
    // Reemplazar el input con el nuevo elemento
    const parent = input.parentElement;
    if (parent) {
      // Para la versión desktop, el input está dentro de un input-group
      const isDesktopLayout = parent.classList.contains('input-group');
      
      if (isDesktopLayout) {
        // En desktop, reemplazar todo el input-group con el autocomplete
        const inputGroupParent = parent.parentElement;
        if (inputGroupParent) {
          const wrapper = document.createElement('div');
          wrapper.className = 'w-100';
          wrapper.appendChild(autocompleteElement);
          
          inputGroupParent.replaceChild(wrapper, parent);
          
          autocompleteElement.style.width = '100%';
          autocompleteElement.style.display = 'block';
        }
      } else {
        // Para mobile (ion-searchbar)
        parent.style.width = '100%';
        parent.style.display = 'block';
        
        parent.insertBefore(autocompleteElement, input);
        input.style.display = 'none';
        
        autocompleteElement.style.width = '100%';
        autocompleteElement.style.display = 'block';
      }
    }

    this.autocomplete = autocompleteElement;

    // Escuchar cuando se selecciona un lugar
    autocompleteElement.addEventListener('gmp-select', async (event: any) => {
      const placePrediction = event.placePrediction;
      
      if (placePrediction) {
        // Convertir placePrediction a Place
        const place = placePrediction.toPlace();
        
        await place.fetchFields({ fields: ['location', 'displayName', 'formattedAddress'] });
        
        if (place.location) {
          const location: LatLng = {
            lat: place.location.lat(),
            lng: place.location.lng(),
          };
          
          this.selectedLocation = location;
          this.selectedAddress = place.formattedAddress || place.displayName || '';
          
          // Centrar el mapa en la nueva ubicación
          this.map?.setCenter(location);
          this.map?.setZoom(17);
          
          // Actualizar posición del marcador (AdvancedMarkerElement)
          if (this.marker) {
            this.marker.position = new google.maps.LatLng(location.lat, location.lng);
          }
          
          this.cdr.detectChanges();
        }
      }
    });
  }

  getCurrentPosition(): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalización no disponible'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => resolve(position),
        (error) => reject(error),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    });
  }

  async centerOnCurrentLocation() {
    if (!this.map) return;

    this.isLoadingLocation = true;
    try {
      const position = await this.getCurrentPosition();
      const currentLocation: LatLng = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      this.selectedLocation = currentLocation;
      this.map.setCenter(currentLocation);
      if (this.marker) {
        // AdvancedMarkerElement usa propiedad 'position' directamente con LatLng
        this.marker.position = new google.maps.LatLng(currentLocation.lat, currentLocation.lng);
      }
      this.cdr.detectChanges();
    } catch (error) {
      // Error obteniendo ubicación
    } finally {
      this.isLoadingLocation = false;
    }
  }

  async showToast(message: string, color: 'success' | 'danger' = 'danger') {
    const toast = await this.toastController.create({
      message: message,
      duration: 3000,
      position: 'bottom',
      color: color,
      buttons: [
        {
          text: 'OK',
          role: 'cancel'
        }
      ]
    });
    await toast.present();
  }

  async confirmLocation() {
    if (!this.selectedLocation || !this.phone) {
      return;
    }

    this.isSavingAddress = true;

    try {
      const addressRequest: CustomerAddressAddRequest = {
        address: this.selectedAddress || `Lat: ${this.selectedLocation.lat.toFixed(6)}, Lng: ${this.selectedLocation.lng.toFixed(6)}`,
        latitude: this.selectedLocation.lat,
        longitude: this.selectedLocation.lng
      };

      this.clickeatService.addressAdd(this.phone, addressRequest).subscribe({
        next: async (response: CustomerAddressAddResponse) => {
          this.isSavingAddress = false;
          this.cdr.detectChanges();
          
          // En móvil, mostrar toast y redirigir al home
          if (this.isMobile()) {
            await this.showToast('✅ Dirección guardada exitosamente', 'success');
            this.router.navigate(['/']);
          } else {
            // En desktop usar sweetalert2
            await Swal.fire({
              icon: 'success',
              title: 'Dirección guardada',
              text: `ID: ${response.idAddress}`,
              confirmButtonText: 'OK'
            });
            this.router.navigate(['/']);
          }
        },
        error: async (error) => {
          this.isSavingAddress = false;
          this.cdr.detectChanges();
          
          // Mostrar error del API - el API regresa "detail" cuando hay error
          const errorMsg = error.error?.detail || error.message || 'Error desconocido';
          if (this.isMobile()) {
            await this.showToast(`❌ Error guardando dirección: ${errorMsg}`);
          } else {
            await Swal.fire({
              icon: 'error',
              title: 'Error guardando dirección',
              text: errorMsg,
              confirmButtonText: 'OK'
            });
          }
        }
      });
    } catch (error) {
      this.isSavingAddress = false;
      this.cdr.detectChanges();
      
      if (this.isMobile()) {
        await this.showToast('❌ Error al procesar la solicitud');
      } else {
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Error al procesar la solicitud',
          confirmButtonText: 'OK'
        });
      }
    }
  }
}
