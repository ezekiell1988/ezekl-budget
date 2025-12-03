import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'tokenExpiry',
  standalone: true,
  pure: true
})
export class TokenExpiryPipe implements PipeTransform {
  transform(expiresAt?: Date): string {
    if (!expiresAt) return 'Desconocido';

    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();

    if (diff <= 0) return 'Expirado';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  }
}
