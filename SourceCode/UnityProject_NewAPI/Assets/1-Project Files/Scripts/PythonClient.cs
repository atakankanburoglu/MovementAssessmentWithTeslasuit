using System;
using System.Collections;
using System.Threading;
using UnityEngine;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;


public class PythonClient
{
    private Thread senderThread;
    private Thread receiverThread;
    private Queue dataQueue = new Queue();
    private Boolean running = false;
    private DataGateway dataGateway;

    public PythonClient()
    {
        dataGateway = GameObject.Find("DataGateway").GetComponent<DataGateway>();
        senderThread = new Thread(RunSend);
        senderThread.Start();
        receiverThread = new Thread(RunReceive);
        receiverThread.Start();
        running = true;
    }

    private void RunSend()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (PublisherSocket publisher = new PublisherSocket())
        {
            publisher.Bind("tcp://*:5556");
            while (running)
            {
                if (dataQueue.Count > 0)
                {
                    FrameDataObject dataToSend = (FrameDataObject)dataQueue.Dequeue();
                    string frame = dataToSend.ToString();
                    publisher.SendFrame(frame);
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
            subscriber.Connect("tcp://localhost:6667");
            //subscriber.Subscribe("ErrorResponseStream");
            subscriber.SubscribeToAnyTopic();

            while (running)
            {
                string payload = subscriber.ReceiveFrameString();
                String[] values = payload.Split(' ');
                String topic = values[0];
                string message = values[1];

                if(topic == "RelativeError")
                {
                    dataGateway.OnExcerciseRecognized(message);
                }
                if (topic == "ExerciseList")
                {
                    dataGateway.OnRecordedExercisesListReceived(message);
                }
                Thread.Sleep(1);
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    public void PushData(FrameDataObject data)
    {
        dataQueue.Enqueue(data);
    }

    public void Stop()
    {
        running = false;
        // block main thread, wait for _runnerThread to finish its job first, so we can be sure that 
        // _runnerThread will end before main thread end
        senderThread.Join();
        receiverThread.Join();
    }
}