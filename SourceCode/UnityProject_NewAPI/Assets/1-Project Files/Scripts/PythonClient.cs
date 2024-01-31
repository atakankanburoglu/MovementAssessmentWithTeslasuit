using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Threading;
using UnityEngine;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using Debug = UnityEngine.Debug;
using System.IO;
using Newtonsoft.Json;


public class PythonClient
{
    private Thread _senderThread;
    private Thread _receiverThread;
    private Queue replayInfoQueue = new Queue();
    private Boolean running = false;

    //for Finishing Training Data Transfer
    private Boolean finished = false;
    private SampleType sampleType;

    //for Model Creation and Usage
    private Boolean createModel = false;
    private Boolean chooseModel = false;
    private String modelInfo;

    //private MotionFeedback _motionFeedback;
    //private MocapJoints _mocapJoints;
    private DataGateway _dataGateway;

    public PythonClient()
    {
        //_mocapJoints = MocapJoints.GetInstance();
        //_motionFeedback = GameObject.Find("Teslasuit_Man").GetComponent<MotionFeedback>();
        _dataGateway = GameObject.Find("DataGateway").GetComponent<DataGateway>();
        _senderThread = new Thread(RunSend);
        _senderThread.Start();
        _receiverThread = new Thread(RunReceive);
        _receiverThread.Start();
        running = true;
    }

    private void RunSend()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (PublisherSocket publisher = new PublisherSocket())
        {
            publisher.Bind("tcp://*:5555");
            while (running)
            {
                if (replayInfoQueue.Count > 0)
                {

                    ImuDataObject dataToSend = (ImuDataObject)replayInfoQueue.Dequeue();
                    string csv = dataToSend.ToCSV(";", filtered: true);
                    publisher.SendFrame("ImuDataStream " + csv);
                }
                if(finished)
                {
                    publisher.SendFrame("TrainingFinished " + sampleType);
                    finished = false;
                }
                if (createModel)
                {
                    publisher.SendFrame("CreateModel " + modelInfo);
                    createModel = false;
                }
                if (chooseModel)
                {
                    publisher.SendFrame("Model " + modelInfo);
                    chooseModel = false;
                }
                Thread.Sleep(1);
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    private void RunReceive()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (SubscriberSocket subscriber = new SubscriberSocket())
        {
            subscriber.Connect("tcp://localhost:6666");
            subscriber.Subscribe("ErrorResponseStream");

            while (running)
            {
                string payload = subscriber.ReceiveFrameString();
                String[] values = payload.Split(' ');
                string message = values[1];
                values = message.Split(',');

                _dataGateway.onExcerciseRecognized(values[0]);
                //PerformanceAnalyzer.GetInstance().DataPointReceived((int)float.Parse(values[1], CultureInfo.InvariantCulture));

                //TrainingType recognizedExercise = (TrainingType)Enum.Parse(typeof(TrainingType), values[0], true);
                //if (recognizedExercise != null)
                //{
                //    _dataGateway.recognizedExercise = recognizedExercise;
                //    Debug.Log($"Recognized: {recognizedExercise}");
                //}


                //int indexOffset = 2;
                //Dictionary<String, Vector3> motionErrors = new Dictionary<string, Vector3>();

                //for (var i = 0; i < _mocapJoints.JointNames.Count; i++)
                //{
                //    Vector3 error = new Vector3(
                //        float.Parse(values[indexOffset + i * 3], CultureInfo.InvariantCulture),
                //        float.Parse(values[indexOffset + i * 3 + 1], CultureInfo.InvariantCulture),
                //        float.Parse(values[indexOffset + i * 3 + 2], CultureInfo.InvariantCulture));

                //    if (!error.Equals(Vector3.zero))
                //    {
                //        motionErrors[_mocapJoints.JointNames[i]] = error;
                //    }
                //}

                //_motionFeedback.MotionError = motionErrors;
                //PerformanceAnalyzer.GetInstance().ErrorReceived((int)float.Parse(values[1], CultureInfo.InvariantCulture));
                Thread.Sleep(1);
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    public void pushSuitData(ImuDataObject data)
    {
        replayInfoQueue.Enqueue(data);
    }

    public void finishSuitTrainingData(SampleType sampleType)
    {
        finished = true;
        this.sampleType = sampleType;
    }

    public void createNewModel(String subjectIds, TrainingType trainingType, Algorithm algorithm)
    {
        createModel = true;
        modelInfo = subjectIds + "_" + trainingType + "_" + algorithm;
    }

    public void chooseModelForTesting(TrainingType trainingType, Algorithm algorithm)
    {
        chooseModel = true;
        modelInfo = trainingType + "_" + algorithm;
    }

    public void Stop()
    {
        running = false;
        // block main thread, wait for _runnerThread to finish its job first, so we can be sure that 
        // _runnerThread will end before main thread end
        _senderThread.Join();
        _receiverThread.Join();
    }
}