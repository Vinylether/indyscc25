#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <pthread.h>
#include <string.h>
#include "data.h"

typedef struct {
	int type;
    int startSample;
    int endSample;
	double beamStart;
	double beamEnd;
    double* beam;
    double* startTimes;
} ThreadData;

void* beamSamples(void* args)
{
	ThreadData* data = (ThreadData*) args;
	double* beam = data->beam;
	double* startTimes = data->startTimes;

	for (int i = 0; i < WAVEFORM_COUNT; i++)
	{
		int waveformStartSample;
		int beamStartSample = data->startSample;
		if (data->beamStart > startTimes[i])
		{
			waveformStartSample = (int) ((data->beamStart - startTimes[i]) * SAMPLE_RATE + 1 + data->startSample); 
		}
		else
		{
			int offset = (int) ((startTimes[i] - data->beamStart) * SAMPLE_RATE + 1);
			if (data->startSample == 0)
			{
				waveformStartSample = 0;
				beamStartSample = offset;
			}
			else 
			{
				waveformStartSample = data->startSample - offset;
			}
		}

		for (int j = beamStartSample; j < data->endSample; j++)
		{
			double sample = WAVEFORMS[i][waveformStartSample + j];
			if (data->type == 2)
			{
				sample = fabs(sample);
			}

			beam[beamStartSample + j] += sample;
		}
	}

	for (int i = data->startSample; i < data->endSample; i++)
	{
		beam[i] /= WAVEFORM_COUNT;
	}

	return NULL;
}

void beam( int type, int* length, double** beam, int numThreads )
{
	double latSum = 0.0;
    double lonSum = 0.0;
	double startTime = 1708968343.0;
	double endTime = 1708969543.025;
	printf("StartTime: %f, EndTime: %f, Length: %f, SampleCount: %d\n", startTime, endTime, (endTime - startTime), SAMPLE_COUNT);
    for (int i = 0; i < WAVEFORM_COUNT; i++)
    {
        latSum += LATITUDES[i];
        lonSum += LONGITUDES[i];
    }

    double averageLat = latSum / WAVEFORM_COUNT;
    double averageLon = lonSum / WAVEFORM_COUNT;

    double *shiftedStartTimes = (double*) malloc(WAVEFORM_COUNT * sizeof(double));
    double *shiftedEndTimes = (double*) malloc(WAVEFORM_COUNT * sizeof(double));
	double slowDeg = SLOWNESS * KM_PER_DEGREE;
    double slowX = slowDeg * sin(BACK_AZIMUTH * M_PI / 180.0); 
    double slowY = slowDeg * cos(BACK_AZIMUTH * M_PI / 180.0);
    for (int i = 0; i < WAVEFORM_COUNT; i++)
    {
        double latRel = LATITUDES[i] - averageLat;
        double lonRel = LONGITUDES[i] - averageLon;
        double timeShift = (slowX * lonRel + slowY * latRel);
        shiftedStartTimes[i] = startTime + timeShift;
        shiftedEndTimes[i] = endTime + timeShift;
    }
	
    double beamStart = -INFINITY;
    double beamEnd = INFINITY;
	for (int i = 0; i < WAVEFORM_COUNT; i++)
	{
		if (shiftedStartTimes[i] > beamStart)
        {
            beamStart = shiftedStartTimes[i];
        }

        if (shiftedEndTimes[i] < beamEnd)
        {
            beamEnd = shiftedEndTimes[i];
        }
	}

    printf("Beam start: %f, Beam end: %f, length: %f\n", beamStart, beamEnd, (beamEnd - beamStart));
    *length = (int) ((beamEnd - beamStart) * SAMPLE_RATE + 1);
    *beam = (double*) calloc(*length, sizeof(double));

	if (numThreads == 0)
	{
		ThreadData threadData[1];
		threadData[0].startSample = 0;
		threadData[0].endSample = *length;
		threadData[0].beamStart = beamStart;
		threadData[0].beamEnd = beamEnd;
		threadData[0].beam = *beam;
		threadData[0].startTimes = shiftedStartTimes;
		beamSamples(threadData);
	}
	else 
	{
		pthread_t threads[numThreads];
		ThreadData threadData[numThreads];
		int samplesPerThread = *length / numThreads;
		for (int t = 0; t < numThreads; t++)
		{ 
			threadData[t].startSample = t == 0 ? 0 : t * samplesPerThread + 1;
			threadData[t].endSample = t == numThreads - 1 ? *length : (t + 1) * samplesPerThread + 1;
			threadData[t].beamStart = beamStart;
			threadData[t].beamEnd = beamEnd;
			threadData[t].beam = *beam;
			threadData[t].startTimes = shiftedStartTimes;
			
			pthread_create(&threads[t], NULL, beamSamples, (void*) &threadData);
		}

		for (int t = 0; t < numThreads; t++)
		{
			pthread_join(threads[t], NULL);
		}
	}

	free(shiftedStartTimes);
	free(shiftedEndTimes);
}

void maxAndAverage(int waveformLength, double *waveform, double* max, double* average)
{
	*max = -INFINITY;
	*average = 0;
	for (int i = 0; i < waveformLength; i++)
	{
		*average += waveform[i];
		if (waveform[i] > *max)
			*max = waveform[i];
	}

	*average /= waveformLength;
}

int stalta(int staLength, int ltaLength, int waveformLength, double *waveform, double threshold)
{
	int inSignal = 0;
	int numSignals = 0;
	for (int i = ltaLength; i < waveformLength; i++)
	{
		double sta = 0.0;
		for (int j = i - staLength; j <= i; j++)
		{
			sta += waveform[j];
		}

		sta /= staLength;

		double lta = 0.0;
		for (int j = i - ltaLength; j <= i; j++)
		{
			lta += waveform[j];
		}

		lta /= ltaLength;
		double value = sta / lta;
		if (!inSignal && value > threshold)
		{
			printf("Signal found starting at: %d\n", i);
			inSignal = 1;
			numSignals++;
		}

		if (inSignal && value <= threshold)
		{
			printf("Signal ended at: %d\n", i);
			inSignal = 0;
		}
	}

	return numSignals;
}

int main(int argc, char* argv[])
{
	if (argc != 3)
	{
		fprintf(stderr, "Failed: expected 2 arguments, received %d", argc - 1);
		exit(1);
	}
	
	if (strcmp("-t", argv[1]) != 0)
	{
		fprintf(stderr, "Failed: unexpected argument: %s\n", argv[1]);
		exit(1);
	}

	int numThreads = atoi(argv[2]);

	struct timeval start;
    gettimeofday(&start, NULL);

	int coherentLength;
	double *coherentBeam;
	beam(1, &coherentLength, &coherentBeam, numThreads - 1);

	int incoherentLength;
	double *incoherentBeam;
	beam(2, &incoherentLength, &incoherentBeam, numThreads - 1);

	free(coherentBeam);
	free(incoherentBeam);

    struct timeval stop;
    gettimeofday(&stop, NULL);
    long micros = (stop.tv_sec - start.tv_sec) * 1000000 + stop.tv_usec - start.tv_usec;
    float seconds = (float) micros / 1000000.0;
    printf("Total run time: %lu us (%.6f s)\n", micros, seconds);
}