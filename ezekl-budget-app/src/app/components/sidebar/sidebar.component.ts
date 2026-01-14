import { Component, Input, Output, EventEmitter, ElementRef, HostListener, ViewChild, OnInit, AfterViewChecked, AfterViewInit, ChangeDetectorRef, effect } 		 from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { NgScrollbarModule } from 'ngx-scrollbar';
import { 
  IonMenu,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonMenuToggle,
  IonButton,
  IonButtons,
  MenuController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { 
  homeOutline, 
  personOutline, 
  settingsOutline,
  logOutOutline,
  walletOutline,
  statsChartOutline,
  documentTextOutline,
  businessOutline,
  chevronForwardOutline,
  chevronDownOutline,
  folderOutline,
  documentOutline,
  closeOutline,
  checkmarkCircle,
  ellipseOutline
} from 'ionicons/icons';
import { slideUp } from '../../composables/slideUp.js';
import { slideToggle } from '../../composables/slideToggle.js';
import { AppMenuService } from '../../service/app-menus.service';
import { AppSettings } from '../../service/app-settings.service';
import { AuthService, LoggerService, Logger } from '../../service';
import { MenuStateService } from '../../service/menu-state.service';
import { FloatSubMenuComponent } from '../float-sub-menu/float-sub-menu.component';
import { ResponsiveComponent } from '../../shared/responsive-component.base';
import { PlatformMode } from '../../service/platform-detector.service';

@Component({
  selector: 'sidebar',
  templateUrl: './sidebar.component.html',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    NgScrollbarModule, 
    FloatSubMenuComponent,
    IonMenu,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonList,
    IonItem,
    IonLabel,
    IonIcon,
    IonMenuToggle,
    IonButton,
    IonButtons
  ]
})

export class SidebarComponent extends ResponsiveComponent implements AfterViewChecked {
	private readonly logger: Logger;
	menus: any[] = [];
	currentUser: any = null;
	// Flag para controlar el renderizado del ion-menu
	showIonMenu = false;
	// Flag para indicar si el componente está inicializado
	private isInitialized = false;
	
  @ViewChild('sidebarScrollbar', { static: false }) private sidebarScrollbar: ElementRef;
	@Output() appSidebarMinifiedToggled = new EventEmitter<boolean>();
	@Output() hideMobileSidebar = new EventEmitter<boolean>();
	@Output() setPageFloatSubMenu = new EventEmitter();
	
	@Output() appSidebarMobileToggled = new EventEmitter<boolean>();
	@Input() appSidebarTransparent;
	@Input() appSidebarGrid;
	@Input() appSidebarFixed;
	@Input() appSidebarMinified;
	
	appSidebarFloatSubMenu;
	appSidebarFloatSubMenuHide;
	appSidebarFloatSubMenuHideTime = 250;
	appSidebarFloatSubMenuTop;
	appSidebarFloatSubMenuLeft = '60px';
	appSidebarFloatSubMenuRight;
  appSidebarFloatSubMenuBottom;
  appSidebarFloatSubMenuArrowTop;
  appSidebarFloatSubMenuArrowBottom;
  appSidebarFloatSubMenuLineTop;
  appSidebarFloatSubMenuLineBottom;
  appSidebarFloatSubMenuOffset;

	mobileMode;
	desktopMode;
	scrollTop;
	
  toggleNavProfile(e) {
		e.preventDefault();
	
		var targetSidebar = <HTMLElement>document.querySelector('.app-sidebar:not(.app-sidebar-end)');
		var targetMenu = e.target.closest('.menu-profile');
		var targetProfile = <HTMLElement>document.querySelector('#appSidebarProfileMenu');
		var expandTime = (targetSidebar && targetSidebar.getAttribute('data-disable-slide-animation')) ? 0 : 250;
	
		if (targetProfile && targetProfile.style) {
			if (targetProfile.style.display == 'block') {
				targetMenu.classList.remove('active');
			} else {
				targetMenu.classList.add('active');
			}
			slideToggle(targetProfile, expandTime);
			targetProfile.classList.toggle('expand');
		}
  }

	toggleAppSidebarMinified() {
		// Alternar el estado actual en lugar de siempre emitir true
		this.appSidebarMinifiedToggled.emit(!this.appSettings.appSidebarMinified);
		this.scrollTop = 40;
	}
	
	toggleAppSidebarMobile() {
		this.appSidebarMobileToggled.emit(true);
	}

	calculateAppSidebarFloatSubMenuPosition() {
		var targetTop = this.appSidebarFloatSubMenuOffset.top;
    var direction = document.documentElement.getAttribute('dir');
    var windowHeight = window.innerHeight;

    setTimeout(() => {
      let targetElm = <HTMLElement> document.querySelector('.app-sidebar-float-submenu-container');
      let targetSidebar = <HTMLElement> document.getElementById('sidebar');
      var targetHeight = targetElm.offsetHeight;
      
      this.appSidebarFloatSubMenuLeft = 'auto';
			this.appSidebarFloatSubMenuRight = 'auto';
			
			if (direction === 'rtl') {
				const sidebarRightOffset = window.innerWidth - (targetSidebar.offsetLeft + targetSidebar.offsetWidth);
				this.appSidebarFloatSubMenuRight = (window.innerWidth - targetSidebar.offsetLeft) + 'px';
				this.logger.debug('appSidebarFloatSubMenuRight:', this.appSidebarFloatSubMenuRight);
			} else {
				this.appSidebarFloatSubMenuLeft = (this.appSidebarFloatSubMenuOffset.width + targetSidebar.offsetLeft) + 'px';
			}
      
      if ((windowHeight - targetTop) > targetHeight) {
        this.appSidebarFloatSubMenuTop = this.appSidebarFloatSubMenuOffset.top + 'px';
        this.appSidebarFloatSubMenuBottom = 'auto';
        this.appSidebarFloatSubMenuArrowTop = '20px';
        this.appSidebarFloatSubMenuArrowBottom = 'auto';
        this.appSidebarFloatSubMenuLineTop = '20px';
        this.appSidebarFloatSubMenuLineBottom = 'auto';
      } else {
        this.appSidebarFloatSubMenuTop = 'auto';
        this.appSidebarFloatSubMenuBottom = '0';

        var arrowBottom = (windowHeight - targetTop) - 21;
        this.appSidebarFloatSubMenuArrowTop = 'auto';
        this.appSidebarFloatSubMenuArrowBottom = arrowBottom + 'px';
        this.appSidebarFloatSubMenuLineTop = '20px';
        this.appSidebarFloatSubMenuLineBottom = arrowBottom + 'px';
      }
    }, 0);
	}

	showAppSidebarFloatSubMenu(menu, e) {
	  if (this.appSettings.appSidebarMinified) {
      clearTimeout(this.appSidebarFloatSubMenuHide);

      this.appSidebarFloatSubMenu = menu;
      this.appSidebarFloatSubMenuOffset = e.target.getBoundingClientRect();
      this.calculateAppSidebarFloatSubMenuPosition();
    }
	}

	hideAppSidebarFloatSubMenu() {
	  this.appSidebarFloatSubMenuHide = setTimeout(() => {
	    this.appSidebarFloatSubMenu = '';
	  }, this.appSidebarFloatSubMenuHideTime);
	}

	remainAppSidebarFloatSubMenu() {
		clearTimeout(this.appSidebarFloatSubMenuHide);
	}

	appSidebarSearch(e: any) {
	  var targetValue = e.target.value;
	      targetValue = targetValue.toLowerCase();

    if (targetValue) {
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .menu > .menu-item:not(.menu-profile):not(.menu-header):not(.menu-search), .app-sidebar:not(.app-sidebar-end) .menu-submenu > .menu-item'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.add('d-none');
				});
			}
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .has-text'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.remove('has-text');
				});
			}
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .expand'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.remove('expand');
				});
			}
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .menu > .menu-item:not(.menu-profile):not(.menu-header):not(.menu-search) > .menu-link, .app-sidebar .menu-submenu > .menu-item > .menu-link'));
			if (elms) {
				elms.map(function(elm) {
					var targetText = elm.textContent;
							targetText = targetText.toLowerCase();
					if (targetText.search(targetValue) > -1) {
						var targetElm = elm.closest('.menu-item');
						if (targetElm) {
							targetElm.classList.remove('d-none');
							targetElm.classList.add('has-text');
						}
					
						var targetElm = elm.closest('.menu-item.has-sub');
						if (targetElm) {
							var targetElm = targetElm.querySelector('.menu-submenu .menu-item.d-none');
							if (targetElm) {
								targetElm.classList.remove('d-none');
							}
						}
					
						var targetElm = elm.closest('.menu-submenu');
						if (targetElm) {
							targetElm.style.display = 'block';
						
							var targetElm = targetElm.querySelector('.menu-item:not(.has-text)');
							if (targetElm) {
								targetElm.classList.add('d-none');
							}
						
							var targetElm = elm.closest('.has-sub:not(.has-text)');
							if (targetElm) {
								targetElm.classList.remove('d-none');
								targetElm.classList.add('expand');
							
								var targetElm = targetElm.closest('.has-sub:not(.has-text)');
								if (targetElm) {
									targetElm.classList.remove('d-none');
									targetElm.classList.add('expand');
								}
							}
						}
					}
				});
			}
		} else {
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .menu > .menu-item:not(.menu-profile):not(.menu-header):not(.menu-search).has-sub .menu-submenu'));
			if (elms) {
				elms.map(function(elm) {
					elm.removeAttribute('style');
				});
			}
		
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .menu > .menu-item:not(.menu-profile):not(.menu-header):not(.menu-search)'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.remove('d-none');
				});
			}
		
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .menu-submenu > .menu-item'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.remove('d-none');
				});
			}
		
			var elms = [].slice.call(document.querySelectorAll('.app-sidebar:not(.app-sidebar-end) .expand'));
			if (elms) {
				elms.map(function(elm) {
					elm.classList.remove('expand');
				});
			}
		}
  }

  @HostListener('scroll', ['$event'])
  onScroll(event) {
    this.scrollTop = (this.appSettings.appSidebarMinified) ? event.srcElement.scrollTop + 40 : 0;
    if (typeof(Storage) !== 'undefined') {
      localStorage.setItem('sidebarScroll', event.srcElement.scrollTop);
    }
  }

  @HostListener('window:resize', ['$event'])
  onResize(event) {
    if (window.innerWidth <= 767) {
      this.mobileMode = true;
      this.desktopMode = false;
    } else {
      this.mobileMode = false;
      this.desktopMode = true;
    }
  }

  ngAfterViewChecked() {
    if (typeof(Storage) !== 'undefined' && localStorage.sidebarScroll) {
      if (this.sidebarScrollbar && this.sidebarScrollbar.nativeElement) {
        this.sidebarScrollbar.nativeElement.scrollTop = localStorage.sidebarScroll;
      }
    }
  }
  
  ngAfterViewInit() {
    var handleSidebarMenuToggle = function(menus, expandTime) {
			menus.map(function(menu) {
				menu.onclick = function(e) {
					e.preventDefault();
					var target = this.nextElementSibling;
	
					menus.map(function(m) {
						var otherTarget = m.nextElementSibling;
						if (otherTarget !== target) {
							slideUp(otherTarget, expandTime);
							otherTarget.closest('.menu-item').classList.remove('expand');
							otherTarget.closest('.menu-item').classList.add('closed');
						}
					});
	
					var targetItemElm = target.closest('.menu-item');
			
					if (targetItemElm.classList.contains('expand') || (targetItemElm.classList.contains('active') && !target.style.display)) {
						targetItemElm.classList.remove('expand');
						targetItemElm.classList.add('closed');
						slideToggle(target, expandTime);
					} else {
						targetItemElm.classList.add('expand');
						targetItemElm.classList.remove('closed');
						slideToggle(target, expandTime);
					}
				}
			});
		};
	
		var targetSidebar       = document.querySelector('.app-sidebar:not(.app-sidebar-end)');
		var expandTime          = (targetSidebar && targetSidebar.getAttribute('data-disable-slide-animation')) ? 0 : 300;
		var disableAutoCollapse = (targetSidebar && targetSidebar.getAttribute('data-disable-auto-collapse')) ? 1 : 0;
	
		var menuBaseSelector = '.app-sidebar .menu > .menu-item.has-sub';
		var submenuBaseSelector = ' > .menu-submenu > .menu-item.has-sub';

		// menu
		var menuLinkSelector =  menuBaseSelector + ' > .menu-link';
		var menus = [].slice.call(document.querySelectorAll(menuLinkSelector));
		handleSidebarMenuToggle(menus, expandTime);

		// submenu lvl 1
		var submenuLvl1Selector = menuBaseSelector + submenuBaseSelector;
		var submenusLvl1 = [].slice.call(document.querySelectorAll(submenuLvl1Selector + ' > .menu-link'));
		handleSidebarMenuToggle(submenusLvl1, expandTime);

		// submenu lvl 2
		var submenuLvl2Selector = menuBaseSelector + submenuBaseSelector + submenuBaseSelector;
		var submenusLvl2 = [].slice.call(document.querySelectorAll(submenuLvl2Selector + ' > .menu-link'));
		handleSidebarMenuToggle(submenusLvl2, expandTime);
		
  }
  
  
	ngOnInit() {
		this.menus = this.appMenuService.getAppMenus();
		this.initializeMobileMenuState(this.menus);
		
		// Escuchar cambios de navegación para actualizar estado del menú
		this.router.events.pipe(
			filter(event => event instanceof NavigationEnd)
		).subscribe(() => {
			// Reinicializar el estado del menú cuando cambie la ruta
			this.initializeMobileMenuState(this.menus);
			this.cdr.detectChanges();
		});
		
		// Notificar al servicio cuando el menú del sidebar se abre/cierra
		// Usamos los eventos del DOM de ion-menu
		document.addEventListener('ionDidOpen', (event: any) => {
			if (event.target.menuId === 'main-menu') {
				this.menuStateService.setSidebarMenuState(true);
				this.logger.debug('Menu sidebar abierto');
			}
		});
		
		document.addEventListener('ionDidClose', (event: any) => {
			if (event.target.menuId === 'main-menu') {
				// Pequeño delay para asegurar que la navegación se complete primero
				setTimeout(() => {
					this.menuStateService.setSidebarMenuState(false);
					this.logger.debug('Menu sidebar cerrado');
				}, 50);
			}
		});
	}

	private initializeMobileMenuState(items: any[]): void {
		// Obtener la URL actual
		const currentUrl = this.router.url;
		
		// Inicializar el estado de expansión para cada item con submenú
		items.forEach(item => {
			if (item.submenu) {
				// Expandir solo si contiene la ruta activa
				item.expanded = this.menuContainsActiveRoute(item, currentUrl);
				this.initializeMobileMenuState(item.submenu); // Recursivo
			}
		});
	}

	private menuContainsActiveRoute(menuItem: any, currentUrl: string): boolean {
		// Si el item tiene una URL y coincide con la actual
		if (menuItem.url && currentUrl.startsWith(menuItem.url)) {
			return true;
		}
		
		// Si el item tiene submenú, verificar recursivamente
		if (menuItem.submenu) {
			return menuItem.submenu.some((subItem: any) => 
				this.menuContainsActiveRoute(subItem, currentUrl)
			);
		}
		
		return false;
	}

	toggleMobileSubmenu(item: any): void {
		// Alternar el estado de expansión
		item.expanded = !item.expanded;
	}

	expandCollapseSubmenu(currentMenu: any, allMenus: any[], rla: any): void {
		// Colapsar todos los otros menús del mismo nivel
		allMenus.forEach(menu => {
			if (menu !== currentMenu && menu.state !== 'active') {
				menu.state = 'collapsed';
			}
		});

		// Alternar el estado del menú actual
		if (currentMenu.state === 'expand' || (rla.isActive && currentMenu.state !== 'collapsed')) {
			currentMenu.state = 'collapsed';
		} else {
			currentMenu.state = 'expand';
		}
	}

	async closeMenu(): Promise<void> {
		// Cerrar el menú lateral
		await this.menuController.close('main-menu');
	}

	isAuthenticated(): boolean {
		return this.authService.isAuthenticated();
	}

	private mapIconToIonic(colorAdminIcon: string): string {
		// Mapear íconos de FontAwesome a Ionicons
		const iconMap: { [key: string]: string } = {
			'fa fa-home': 'home-outline',
			'fa fa-user': 'person-outline',
			'fa fa-cog': 'settings-outline',
			'fa fa-wallet': 'wallet-outline',
			'fa fa-chart-line': 'stats-chart-outline',
			'fa fa-file': 'document-text-outline',
			'fa fa-building': 'business-outline',
			'fas fa-home': 'home-outline',
			'fas fa-user': 'person-outline',
			'bi bi-house': 'home-outline',
			'bi bi-person': 'person-outline',
		};

		return iconMap[colorAdminIcon] || 'ellipse-outline';
	}

	logout(): void {
		// Llamar al servicio de autenticación para cerrar sesión
		this.authService.logout().subscribe({
			next: () => {
				this.logger.success('Sesión cerrada exitosamente');
				// El servicio ya redirige al login
			},
			error: (error) => {
				this.logger.error('Error al cerrar sesión:', error);
				// Cerrar sesión localmente aunque falle el backend
				this.authService.clearSession();
			}
		});
	}

  constructor(
    private eRef: ElementRef, 
    public appSettings: AppSettings, 
    private appMenuService: AppMenuService, 
    private menuController: MenuController, 
    private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private menuStateService: MenuStateService,
    private router: Router,
    loggerService: LoggerService
  ) {
    super();
    this.logger = loggerService.getLogger('SidebarComponent');
    
    // Registrar íconos de Ionicons
    addIcons({
      homeOutline,
      personOutline,
      settingsOutline,
      logOutOutline,
      walletOutline,
      statsChartOutline,
      documentTextOutline,
      businessOutline,
      chevronForwardOutline,
      chevronDownOutline,
      folderOutline,
      documentOutline,
      closeOutline,
      checkmarkCircle,
      ellipseOutline
    });
    if (window.innerWidth <= 767) {
      this.mobileMode = true;
      this.desktopMode = false;
    } else {
      this.mobileMode = false;
      this.desktopMode = true;
    }
    
    // Escuchar cambios de usuario autenticado usando effect
    effect(() => {
      this.currentUser = this.authService.currentUser();
      this.updateIonMenuVisibility();
    });
    
    // Marcar como inicializado después de completar el constructor
    this.isInitialized = true;
    
    // Actualizar visibilidad inicial
    this.updateIonMenuVisibility();
  }
  
  /**
   * Hook sobrescrito para actualizar visibilidad del menú al cambiar modo
   */
  protected override onPlatformModeChange(mode: PlatformMode): void {
    // Solo actualizar si el componente está inicializado
    if (this.isInitialized) {
      this.updateIonMenuVisibility();
    }
  }
  
  /**
   * Actualiza la visibilidad del ion-menu según autenticación y modo de plataforma
   */
  private updateIonMenuVisibility(): void {
    // Verificar que authService esté disponible
    if (!this.authService) {
      return;
    }
    
    const isMobileMode = this.platformMode() === 'mobile';
    const isAuthenticated = this.authService.isAuthenticated();
    
    if (isMobileMode && isAuthenticated) {
      // Retrasar el renderizado del ion-menu para asegurar que main-content exista
      setTimeout(() => {
        this.showIonMenu = true;
      }, 100);
    } else {
      this.showIonMenu = false;
    }
  }
}
