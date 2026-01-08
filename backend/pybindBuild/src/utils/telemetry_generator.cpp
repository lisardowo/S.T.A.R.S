#include <fstream>
#include <random>
#include <cmath>

int main() {
    std::ofstream file("data/input/telemetry.csv");
    file << "time,altitude,velocity,accel_x,accel_y,accel_z,temperature,voltage\n";
    std::mt19937 rng(1);
    std::normal_distribution<double> noise(0.0, 0.02);
    double altitude = 800000.0; // meters
    double velocity = 7777.7;   // m/s
    double temperature = 0.0;   // celsius
    double voltage = 10.0;        // volts

    for (long long i = 0; i < 20000; ++i) {  // ~2000k lines, 0.01 MB at least
        altitude += velocity * 0.01 + noise(rng);
        velocity += noise(rng);
        temperature += noise(rng);
        voltage += noise(rng) * 0.01;
        double ax = std::sin(i * 0.01) + noise(rng);
        double ay = std::cos(i * 0.01) + noise(rng);
        double az = noise(rng);
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
