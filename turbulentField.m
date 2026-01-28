[x,y] = meshgrid(linspace(0,2*pi,100));
rho = 7900;
mu = 1e-1;

L = sqrt(max(x).^2 + max(y).^2);

u =  sin(y) + 0.5*cos(3*x).*sin(2*y);
v = -sin(x) + 0.5*sin(3*y).*cos(2*x);


speed = sqrt(u.^2 + v.^2);
Re = rho * speed .* L / mu;

figure
imagesc(x(1,:), y(:,1), Re)
set(gca,'YDir','normal')
colorbar
xlabel('x')
ylabel('y')
title('Re(x,y)')

hold on
quiver(x,y,u,v,'k')
hold off
