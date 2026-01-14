import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";

/**
 * Configuración global de la aplicación
 * Usa BehaviorSubjects para permitir reactividad en Angular 20+
 */
@Injectable({
  providedIn: "root",
})
export class AppSettings {
  // Theme settings
  private _appTheme = new BehaviorSubject<string>("");
  private _appCover = new BehaviorSubject<string>("");
  private _appDarkMode = new BehaviorSubject<boolean>(false);
  private _appEmpty = new BehaviorSubject<boolean>(false);
  private _appGradientEnabled = new BehaviorSubject<boolean>(false);
  private _appBodyWhite = new BehaviorSubject<boolean>(false);
  private _appThemePanelNone = new BehaviorSubject<boolean>(false);
  private _appClass = new BehaviorSubject<string>("");

  // Layout settings
  private _appBoxedLayout = new BehaviorSubject<boolean>(false);
  
  // Header settings
  private _appHeaderNone = new BehaviorSubject<boolean>(false);
  private _appHeaderFixed = new BehaviorSubject<boolean>(true);
  private _appHeaderInverse = new BehaviorSubject<boolean>(false);
  private _appHeaderMegaMenu = new BehaviorSubject<boolean>(false);
  private _appHeaderLanguageBar = new BehaviorSubject<boolean>(false);
  private _appHeaderMegaMenuMobileToggled = new BehaviorSubject<boolean>(false);
  private _appTopMenu = new BehaviorSubject<boolean>(false);
  private _appFooter = new BehaviorSubject<boolean>(false);

  // Sidebar settings
  private _appSidebarEnd = new BehaviorSubject<boolean>(false);
  private _appSidebarTwo = new BehaviorSubject<boolean>(false);
  private _appSidebarNone = new BehaviorSubject<boolean>(false);
  private _appSidebarGrid = new BehaviorSubject<boolean>(false);
  private _appSidebarWide = new BehaviorSubject<boolean>(false);
  private _appSidebarLight = new BehaviorSubject<boolean>(false);
  private _appSidebarFixed = new BehaviorSubject<boolean>(true);
  private _appSidebarSearch = new BehaviorSubject<boolean>(false);
  private _appSidebarMinified = new BehaviorSubject<boolean>(false);
  private _appSidebarCollapsed = new BehaviorSubject<boolean>(false);
  private _appSidebarTransparent = new BehaviorSubject<boolean>(false);
  private _appSidebarMobileToggled = new BehaviorSubject<boolean>(false);
  private _appSidebarRightCollapsed = new BehaviorSubject<boolean>(false);
  private _appSidebarEndToggled = new BehaviorSubject<boolean>(false);
  private _appSidebarEndMobileToggled = new BehaviorSubject<boolean>(false);

  // Content settings
  private _appContentClass = new BehaviorSubject<string>("");
  private _appContentFullHeight = new BehaviorSubject<boolean>(false);
  private _appContentFullWidth = new BehaviorSubject<boolean>(false);

  // Remote Config
  private _remoteConfigCharge = new BehaviorSubject<boolean>(false);
  private _nameCompany = new BehaviorSubject<string>("N/D");
  private _sloganCompany = new BehaviorSubject<string>("N/D");
  private _apiVersion = new BehaviorSubject<string>("0.0.0");
  
  // Loading State
  private _configLoaded = new BehaviorSubject<boolean>(false);
  private _stylesLoaded = new BehaviorSubject<boolean>(false);

  // ============= Getters (valores síncronos) =============

  get appTheme(): string { return this._appTheme.value; }
  get appCover(): string { return this._appCover.value; }
  get appDarkMode(): boolean { return this._appDarkMode.value; }
  get appEmpty(): boolean { return this._appEmpty.value; }
  get appGradientEnabled(): boolean { return this._appGradientEnabled.value; }
  get appBodyWhite(): boolean { return this._appBodyWhite.value; }
  get appThemePanelNone(): boolean { return this._appThemePanelNone.value; }
  get appClass(): string { return this._appClass.value; }

  get appBoxedLayout(): boolean { return this._appBoxedLayout.value; }
  get appHeaderNone(): boolean { return this._appHeaderNone.value; }
  get appHeaderFixed(): boolean { return this._appHeaderFixed.value; }
  get appHeaderInverse(): boolean { return this._appHeaderInverse.value; }
  get appHeaderMegaMenu(): boolean { return this._appHeaderMegaMenu.value; }
  get appHeaderLanguageBar(): boolean { return this._appHeaderLanguageBar.value; }
  get appHeaderMegaMenuMobileToggled(): boolean { return this._appHeaderMegaMenuMobileToggled.value; }
  get appTopMenu(): boolean { return this._appTopMenu.value; }
  get appFooter(): boolean { return this._appFooter.value; }

  get appSidebarEnd(): boolean { return this._appSidebarEnd.value; }
  get appSidebarTwo(): boolean { return this._appSidebarTwo.value; }
  get appSidebarNone(): boolean { return this._appSidebarNone.value; }
  get appSidebarGrid(): boolean { return this._appSidebarGrid.value; }
  get appSidebarWide(): boolean { return this._appSidebarWide.value; }
  get appSidebarLight(): boolean { return this._appSidebarLight.value; }
  get appSidebarFixed(): boolean { return this._appSidebarFixed.value; }
  get appSidebarSearch(): boolean { return this._appSidebarSearch.value; }
  get appSidebarMinified(): boolean { return this._appSidebarMinified.value; }
  get appSidebarCollapsed(): boolean { return this._appSidebarCollapsed.value; }
  get appSidebarTransparent(): boolean { return this._appSidebarTransparent.value; }
  get appSidebarMobileToggled(): boolean { return this._appSidebarMobileToggled.value; }
  get appSidebarRightCollapsed(): boolean { return this._appSidebarRightCollapsed.value; }
  get appSidebarEndToggled(): boolean { return this._appSidebarEndToggled.value; }
  get appSidebarEndMobileToggled(): boolean { return this._appSidebarEndMobileToggled.value; }

  get appContentClass(): string { return this._appContentClass.value; }
  get appContentFullHeight(): boolean { return this._appContentFullHeight.value; }
  get appContentFullWidth(): boolean { return this._appContentFullWidth.value; }

  get remoteConfigCharge(): boolean { return this._remoteConfigCharge.value; }
  get nameCompany(): string { return this._nameCompany.value; }
  get sloganCompany(): string { return this._sloganCompany.value; }
  get apiVersion(): string { return this._apiVersion.value; }
  get configLoaded(): boolean { return this._configLoaded.value; }
  get stylesLoaded(): boolean { return this._stylesLoaded.value; }

  // ============= Setters =============

  set appTheme(value: string) { this._appTheme.next(value); }
  set appCover(value: string) { this._appCover.next(value); }
  set appDarkMode(value: boolean) { this._appDarkMode.next(value); }
  set appEmpty(value: boolean) { this._appEmpty.next(value); }
  set appGradientEnabled(value: boolean) { this._appGradientEnabled.next(value); }
  set appBodyWhite(value: boolean) { this._appBodyWhite.next(value); }
  set appThemePanelNone(value: boolean) { this._appThemePanelNone.next(value); }
  set appClass(value: string) { this._appClass.next(value); }

  set appBoxedLayout(value: boolean) { this._appBoxedLayout.next(value); }
  set appHeaderNone(value: boolean) { this._appHeaderNone.next(value); }
  set appHeaderFixed(value: boolean) { this._appHeaderFixed.next(value); }
  set appHeaderInverse(value: boolean) { this._appHeaderInverse.next(value); }
  set appHeaderMegaMenu(value: boolean) { this._appHeaderMegaMenu.next(value); }
  set appHeaderLanguageBar(value: boolean) { this._appHeaderLanguageBar.next(value); }
  set appHeaderMegaMenuMobileToggled(value: boolean) { this._appHeaderMegaMenuMobileToggled.next(value); }
  set appTopMenu(value: boolean) { this._appTopMenu.next(value); }
  set appFooter(value: boolean) { this._appFooter.next(value); }

  set appSidebarEnd(value: boolean) { this._appSidebarEnd.next(value); }
  set appSidebarTwo(value: boolean) { this._appSidebarTwo.next(value); }
  set appSidebarNone(value: boolean) { this._appSidebarNone.next(value); }
  set appSidebarGrid(value: boolean) { this._appSidebarGrid.next(value); }
  set appSidebarWide(value: boolean) { this._appSidebarWide.next(value); }
  set appSidebarLight(value: boolean) { this._appSidebarLight.next(value); }
  set appSidebarFixed(value: boolean) { this._appSidebarFixed.next(value); }
  set appSidebarSearch(value: boolean) { this._appSidebarSearch.next(value); }
  set appSidebarMinified(value: boolean) { this._appSidebarMinified.next(value); }
  set appSidebarCollapsed(value: boolean) { this._appSidebarCollapsed.next(value); }
  set appSidebarTransparent(value: boolean) { this._appSidebarTransparent.next(value); }
  set appSidebarMobileToggled(value: boolean) { this._appSidebarMobileToggled.next(value); }
  set appSidebarRightCollapsed(value: boolean) { this._appSidebarRightCollapsed.next(value); }
  set appSidebarEndToggled(value: boolean) { this._appSidebarEndToggled.next(value); }
  set appSidebarEndMobileToggled(value: boolean) { this._appSidebarEndMobileToggled.next(value); }

  set appContentClass(value: string) { this._appContentClass.next(value); }
  set appContentFullHeight(value: boolean) { this._appContentFullHeight.next(value); }
  set appContentFullWidth(value: boolean) { this._appContentFullWidth.next(value); }

  set remoteConfigCharge(value: boolean) { this._remoteConfigCharge.next(value); }
  set nameCompany(value: string) { this._nameCompany.next(value); }
  set sloganCompany(value: string) { this._sloganCompany.next(value); }
  set apiVersion(value: string) { this._apiVersion.next(value); }
  set configLoaded(value: boolean) { this._configLoaded.next(value); }
  set stylesLoaded(value: boolean) { this._stylesLoaded.next(value); }

  // ============= Observables (para reactividad) =============

  get appTheme$(): Observable<string> { return this._appTheme.asObservable(); }
  get appDarkMode$(): Observable<boolean> { return this._appDarkMode.asObservable(); }
  get appSidebarCollapsed$(): Observable<boolean> { return this._appSidebarCollapsed.asObservable(); }
  get configLoaded$(): Observable<boolean> { return this._configLoaded.asObservable(); }
  get stylesLoaded$(): Observable<boolean> { return this._stylesLoaded.asObservable(); }
}
