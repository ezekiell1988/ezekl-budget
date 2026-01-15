import { Injectable } from "@angular/core";

/**
 * Interfaz para items del menú
 */
export interface MenuItem {
  icon?: string;
  iconMobile?: string;
  title: string;
  url: string;
  caret?: string;
  submenu?: MenuItem[];
}

/**
 * Servicio para gestionar el menú de la aplicación
 * Siguiendo buenas prácticas de Angular 20+
 */
@Injectable({
  providedIn: "root",
})
export class AppMenuService {
  /**
   * Configuración del menú centralizada
   * Facilita mantenimiento y testing
   */
  private readonly menuConfig: MenuItem[] = [
    {
      icon: "fa fa-sitemap",
      iconMobile: "home-outline",
      title: "Inicio",
      url: "/home",
    },
    {
      icon: "fa fa-flask",
      iconMobile: "flask-outline",
      title: "Demos",
      url: "/demos",
      caret: "true",
      submenu: [
        {
          url: "/voice-shopping",
          title: "Asistente de Voz",
          icon: "fa fa-microphone",
          iconMobile: "mic-outline",
        },
        {
          url: "/voice-review",
          title: "Repaso con Voz",
          icon: "fa fa-book-reader",
          iconMobile: "book-outline",
        },
      ],
    },
    {
      icon: "fa fa-cogs",
      iconMobile: "settings-outline",
      title: "Mantenimiento",
      url: "/maintenance",
      caret: "true",
      submenu: [
        {
          url: "/media-file",
          title: "Archivos",
          icon: "fa fa-file-alt",
          iconMobile: "document-outline",
        },
      ],
    },
    {
      icon: "fa fa-align-left",
      iconMobile: "list-outline",
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
                  icon: "",
                  iconMobile: "",
                },
                {
                  url: "/menu/1/1/2",
                  title: "Menú 3.2",
                  icon: "",
                  iconMobile: "",
                },
              ],
            },
            {
              url: "/menu/1/2",
              title: "Menú 2.2",
              icon: "",
              iconMobile: "",
            },
            {
              url: "/menu/1/3",
              title: "Menú 2.3",
              icon: "",
              iconMobile: "",
            },
          ],
        },
        {
          url: "/menu/2",
          title: "Menú 1.2",
          icon: "",
          iconMobile: "",
        },
        {
          url: "/menu/3",
          title: "Menú 1.3",
          icon: "",
          iconMobile: "",
        },
      ],
    },
  ];

  /**
   * Retorna una copia profunda del menú para evitar mutaciones
   */
  getAppMenus(): MenuItem[] {
    // Retorna deep copy para prevenir mutaciones accidentales
    return JSON.parse(JSON.stringify(this.menuConfig));
  }

  /**
   * Busca un item del menú por URL
   */
  findMenuItemByUrl(url: string): MenuItem | null {
    const search = (items: MenuItem[]): MenuItem | null => {
      for (const item of items) {
        if (item.url === url) return item;
        if (item.submenu) {
          const found = search(item.submenu);
          if (found) return found;
        }
      }
      return null;
    };
    return search(this.menuConfig);
  }

  /**
   * Obtiene todos los items del menú de forma plana
   */
  getFlatMenuItems(): MenuItem[] {
    const flatten = (items: MenuItem[]): MenuItem[] => {
      return items.reduce((acc, item) => {
        acc.push(item);
        if (item.submenu) {
          acc.push(...flatten(item.submenu));
        }
        return acc;
      }, [] as MenuItem[]);
    };
    return flatten(this.menuConfig);
  }
}
