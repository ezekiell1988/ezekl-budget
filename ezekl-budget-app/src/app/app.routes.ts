import { Routes } from "@angular/router";
import {
  HomePage,
  ErrorPage,
  LoginPage,
  AddressPage,
  VoiceShoppingPage,
  VoiceReviewPage,
  MediaFileListPage,
  MediaFileUploadPage,
} from "./pages";
import { AuthGuard } from "./shared/guards";

export const routes: Routes = [
  {
    path: "",
    redirectTo: "/home",
    pathMatch: "full",
  },
  {
    path: "login",
    component: LoginPage,
    data: { title: "Iniciar Sesión" },
  },
  {
    path: "home",
    component: HomePage,
    data: { title: "Home" },
    canActivate: [AuthGuard],
  },
  {
    path: "voice-shopping",
    component: VoiceShoppingPage,
    data: { title: "Asistente de Voz" },
    canActivate: [AuthGuard],
  },
  {
    path: "voice-review",
    component: VoiceReviewPage,
    data: { title: "Repaso con Voz" },
    canActivate: [AuthGuard],
  },
  {
    path: "media-file",
    component: MediaFileListPage,
    data: { title: "Archivos Multimedia" },
    canActivate: [AuthGuard],
  },
  {
    path: "media-file/upload",
    component: MediaFileUploadPage,
    data: { title: "Subir Archivo" },
    canActivate: [AuthGuard],
  },
  {
    path: "address/:phone",
    component: AddressPage,
    data: { title: "Dirección" },
  },
  {
    path: "**",
    component: ErrorPage,
    data: { title: "404 Error" },
  },
];
