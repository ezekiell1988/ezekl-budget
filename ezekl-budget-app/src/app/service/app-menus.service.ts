import { Injectable } from "@angular/core";

@Injectable({
  providedIn: "root",
})
export class AppMenuService {
  getAppMenus() {
    return [
      {
        icon: "fa fa-sitemap",
        title: "Inicio",
        url: "/home",
      },
      {
        icon: "fa fa-align-left",
        title: "Nivel de Menú",
        url: "/menu",
        caret: "true",
        submenu: [
          {
            url: "/menu/1",
            title: "Menú 1.1",
            caret: "true",
            submenu: [
              {
                url: "/menu/1/1",
                title: "Menú 2.1",
                caret: "true",
                submenu: [
                  {
                    url: "/menu/1/1/1",
                    title: "Menú 3.1",
                  },
                  {
                    url: "/menu/1/1/2",
                    title: "Menú 3.2",
                  },
                ],
              },
              {
                url: "/menu/1/2",
                title: "Menú 2.2",
              },
              {
                url: "/menu/1/3",
                title: "Menú 2.3",
              },
            ],
          },
          {
            url: "/menu/2",
            title: "Menú 1.2",
          },
          {
            url: "/menu/3",
            title: "Menú 1.3",
          },
        ],
      },
    ];
  }
}
