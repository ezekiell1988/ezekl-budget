import { Routes } from "@angular/router";
import {
  HomePage,
  ErrorPage,
  LoginPage,
  AddressPage,
  VoiceShoppingPage,
} from "./pages";
import { AuthGuard } from "./shared/guards";

export const routes: Routes = [
  {
    path: "",
    redirectTo: "/login",
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
