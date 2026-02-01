% 2d Laminar flow
clear; clc;

% Gitter
nx = 41; ny = 41;
Lx = 1; Ly = 1;
dx = Lx/(nx-1);
dy = Ly/(ny-1);

% Parameter
rho = 1000; % kg/m^3
rho_l = 1; % kg/m^3
nu = 1e-3;
dt = 0.001;
nt = 18;

% Fields
u = zeros(ny,nx);
v = zeros(ny,nx);
p = ones(ny,nx)*1e+5;

for n = 1:nt
    un = u;
    vn = v;

    % Velocity updates
    u(2:end-1,2:end-1) = un(2:end-1,2:end-1) ...
        - dt/dx * un(2:end-1,2:end-1) .* (un(2:end-1,2:end-1) - un(2:end-1,1:end-2)) ...
        - dt/dy * vn(2:end-1,2:end-1) .* (un(2:end-1,2:end-1) - un(1:end-2,2:end-1)) ...
        - dt/(2*rho*dx) * (p(2:end-1,3:end) - p(2:end-1,1:end-2)) ...
        + nu * (dt/dx^2 * (un(2:end-1,3:end) - 2*un(2:end-1,2:end-1) + un(2:end-1,1:end-2)) ...
        + dt/dy^2 * (un(3:end,2:end-1) - 2*un(2:end-1,2:end-1) + un(1:end-2,2:end-1)));

    v(2:end-1,2:end-1) = vn(2:end-1,2:end-1) ...
        - dt/dx * un(2:end-1,2:end-1) .* (vn(2:end-1,2:end-1) - vn(2:end-1,1:end-2)) ...
        - dt/dy * vn(2:end-1,2:end-1) .* (vn(2:end-1,2:end-1) - vn(1:end-2,2:end-1)) ...
        - dt/(2*rho*dy) * (p(3:end,2:end-1) - p(1:end-2,2:end-1)) ...
        + nu * (dt/dx^2 * (vn(2:end-1,3:end) - 2*vn(2:end-1,2:end-1) + vn(2:end-1,1:end-2)) ...
        + dt/dy^2 * (vn(3:end,2:end-1) - 2*vn(2:end-1,2:end-1) + vn(1:end-2,2:end-1)))...
        + dt * g * (rho_l - rho)./rho_l;

    % Boundaries
    v(26:end,end-20) = -5;
    p(17:25,17:25) = 0.95e+5;

speed = sqrt(u.^2 + v.^2);
Re=rho * speed .* Lx / nu;
divU = u./dx + v./dy;

contourf(speed)
%quiver(u,v)
xlim([0 nx])
ylim([0 ny])
colorbar
xlabel('x')
ylabel('y')
axis equal
drawnow
end
