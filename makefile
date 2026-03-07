CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall

TARGET = triangulation
SRC = triangulation.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
