#include <fstream>
#include <random>
#include <cmath>

int main() {
    std::ofstream file("data/input/telemetry.csv");

    file << "time,altitude,velocity,accel_x,accel_y,accel_z,temperature,voltage\n";

    std::mt19937 rng(1);
    std::normal_distribution<double> noise(0.0, 0.02);

    double altitude = 400000.0; // metros (órbita baja)
    double velocity = 7777.0;   // m/s
    double temperature = 22.0;
    double voltage = 3.7;

    for (int i = 0; i < 200000; ++i) {  // ~200k líneas ≈ 1.3 MB
        altitude += velocity * 0.01 + noise(rng);
        velocity += noise(rng);
        temperature += noise(rng);
        voltage += noise(rng) * 0.001;

        double ax = std::sin(i * 0.01) + noise(rng);
        double ay = std::cos(i * 0.01) + noise(rng);
        double az = -9.81 + noise(rng);

        file << i << ","
             << altitude << ","
             << velocity << ","
             << ax << ","
             << ay << ","
             << az << ","
             << temperature << ","
             << voltage << "\n";
    }

    file.close();
    return 0;
}
