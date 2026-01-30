% 2d Laminar flow
clear; clc;

% Gitter
nx = 41; ny = 41;
Lx = 1; Ly = 1;
dx = Lx/(nx-1);
dy = Ly/(ny-1);

% Parameter
rho = 1000;
nu = 1e-1;
dt = 0.001;
nt = 500;

% Fields
u = zeros(ny,nx);
v = zeros(ny,nx);
p = zeros(ny,nx);

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
        + dt/dy^2 * (vn(3:end,2:end-1) - 2*vn(2:end-1,2:end-1) + vn(1:end-2,2:end-1)));

    % Boundaries (Cavity)
    u(:,1) = 2; u(:,end) = rand;
    u(1,:) = 3; u(end,:) = 0;
    v(:,1) = 8;
    p(1,:) = 0; p(end,:) = 0;
end
speed = sqrt(u.^2 + v.^2);
Re=rho * speed .* Lx / nu;

%Re=Re/max(max(Re));

subplot(1,2,1)
contourf(Re)
colorbar
xlabel('x')
ylabel('y')

subplot(1,2,2)
quiver(u,v)
xlim([0 nx])
ylim([0 ny])
