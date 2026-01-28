clc
clear
close all

%% Wertebereiche festlegen
St = linspace(0.01, 10, 50);     % Stokes-Zahl
Re = linspace(1, 1000, 50);      % Reynolds-Zahl

%% Gitter erzeugen
[St_grid, Re_grid] = meshgrid(St, Re);

%% Zusammenhang definieren (Beispielmodell!)
% HIER ggf. deine echte physikalische Gleichung einsetzen
Eo = St_grid .* sqrt(Re_grid);

%% 3D-Plot
figure
surf(St_grid, Re_grid, Eo)

xlabel('Stokes-Zahl (St)')
ylabel('Reynolds-Zahl (Re)')
zlabel('Eötvös-Zahl (Eo)')

colorbar
shading interp
grid on
view(45,30)
