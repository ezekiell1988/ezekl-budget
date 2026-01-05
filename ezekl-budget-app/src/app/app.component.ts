import { Component, OnInit, OnDestroy, signal, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Subscription } from "rxjs";
import { PlatformDetectorService, PlatformMode } from "./service/platform-detector.service";
import { MobileLayoutComponent } from "./layouts/mobile-layout/mobile-layout.component";
import { DesktopLayoutComponent } from "./layouts/desktop-layout/desktop-layout.component";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  standalone: true,
  imports: [
    CommonModule,
    MobileLayoutComponent,
    DesktopLayoutComponent,
  ],
})
export class AppComponent implements OnInit, OnDestroy {
  // Signals para manejo reactivo del modo de plataforma
  platformMode = signal<PlatformMode>('desktop');
  isMobile = computed(() => this.platformMode() === 'mobile');
  isDesktop = computed(() => this.platformMode() === 'desktop');
  
  private platformSubscription: Subscription | null = null;

  constructor(private platformDetector: PlatformDetectorService) {}

  ngOnInit() {
    // Suscribirse a cambios de modo de plataforma
    this.platformSubscription = this.platformDetector.platformMode$.subscribe(mode => {
      this.platformMode.set(mode);
    });
  }

  ngOnDestroy(): void {
    if (this.platformSubscription) {
      this.platformSubscription.unsubscribe();
    }
  }
}
