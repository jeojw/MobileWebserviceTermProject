package com.example.termproject;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.loader.content.AsyncTaskLoader;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    TextView textView;
    String socketHost = "10.0.2.2";
    int socketPort = 9000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activate_main);

        textView = findViewById(R.id.textView);
    }

    public void onClickDownload(View v) {
        Toast.makeText(this, "서버에서 이미지 목록 불러오는 중...", Toast.LENGTH_SHORT).show();
        new CloudImage().execute();
    }

    private class CloudImage extends AsyncTask<Void, Void, List<Bitmap>> {
        @Override
        protected List<Bitmap> doInBackground(Void... voids) {
            List<Bitmap> bitmapList = new ArrayList<>();

            try (Socket socket = new Socket(socketHost, socketPort)) {
                DataOutputStream dos = new DataOutputStream(socket.getOutputStream());
                DataInputStream dis = new DataInputStream(socket.getInputStream());

                dos.write("GET_IMAGES\n".getBytes());
                dos.flush();

                String jsonStr = dis.readUTF();
                JSONArray aryJson = new JSONArray(jsonStr);

                for (int i = 0; i < aryJson.length(); i++) {
                    JSONObject obj = aryJson.getJSONObject(i);
                    int imgSize = obj.getInt("size");
                    byte[] imgBytes = new byte[imgSize];

                    dis.readFully(imgBytes);
                    Bitmap bitmap = BitmapFactory.decodeByteArray(imgBytes, 0, imgBytes.length);
                    bitmapList.add(bitmap);
                }

            } catch (Exception e) {
                e.printStackTrace();
            }

            return bitmapList;
        }

        @Override
        protected void onPostExecute(List<Bitmap> images) {
            if (images.isEmpty()) {
                textView.setText("불러올 이미지가 없습니다.");
            } else {
                textView.setText("이미지 로드 성공!");
                RecyclerView recyclerView = findViewById(R.id.recyclerView);
                ImageAdapter adapter = new ImageAdapter(images);
                recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));
                recyclerView.setAdapter(adapter);
            }
        }
    }

    // =================== 이미지 업로드 =====================
    public void onClickUpload(View v) {
        new PutPost().execute();
    }

    private class PutPost extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... voids) {
            try (Socket socket = new Socket(socketHost, socketPort)) {
                DataOutputStream dos = new DataOutputStream(socket.getOutputStream());
                DataInputStream dis = new DataInputStream(socket.getInputStream());

                Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.ic_launcher_background);
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                bitmap.compress(Bitmap.CompressFormat.JPEG, 90, baos);
                byte[] imgBytes = baos.toByteArray();

                dos.writeUTF("UPLOAD_IMAGE sample.jpg");
                dos.writeInt(imgBytes.length);
                dos.write(imgBytes);
                dos.flush();

                String response = dis.readUTF();
                return response;

            } catch (Exception e) {
                e.printStackTrace();
                return "Upload Failed: " + e.getMessage();
            }
        }

        @Override
        protected void onPostExecute(String result) {
            Toast.makeText(MainActivity.this, "서버 응답: " + result, Toast.LENGTH_SHORT).show();
        }
    }
}
