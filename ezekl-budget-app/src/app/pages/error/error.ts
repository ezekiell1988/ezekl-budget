import { Component, OnDestroy, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { AppSettings } from "../../service/app-settings.service";

@Component({
  selector: "error",
  templateUrl: "./error.html",
  standalone: true,
  imports: [CommonModule, RouterModule],
})
export class ErrorPage implements OnDestroy {
  constructor(public appSettings: AppSettings) {
    this.appSettings.appEmpty = true;
  }

  ngOnDestroy() {
    this.appSettings.appEmpty = false;
  }
}
