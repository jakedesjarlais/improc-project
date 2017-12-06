
#include <windows.h>
#include <stdio.h> 
#include <string>

#include <cuda.h>
#include "helper_cuda_drvapi.h"

#include <NvFBCLibrary.h>
#include <NvFBC/nvFBCCuda.h>

#include <cuda_runtime_api.h>

#include "Encoder.h"


/***** PROJECT SETTINGS ******/
#define NUM_FRAMES_TO_RECORD 1000
#define ENCODER_BITRATE 8000000
/***** PROJECT SETTINGS ******/

// Note: this will fail if resolution changes
// TODO: re setup encoder so it doesnt


// CUDA kernel for transforming from RGB color space to NV12
extern "C" cudaError launch_CudaARGB2NV12Process(int w,
                                                 int h,
                                                 CUdeviceptr pARGBImage,
                                                 CUdeviceptr pNV12Image);


// Set NvFBC frame grab parameters
void setup_frame_grab_params(NVFBC_CUDA_GRAB_FRAME_PARAMS* frame_grab_params,
                             NvFBCFrameGrabInfo frame_grab_info,
                             CUdeviceptr frame_buffer) {
    memset(&frame_grab_params, 0, sizeof(NVFBC_CUDA_GRAB_FRAME_PARAMS));
    frame_grab_params->dwVersion = NVFBC_CUDA_GRAB_FRAME_PARAMS_VER;
    fbcCudaGrabParams->pCUDADeviceBuffer = (void*) frame_buffer;
    fbcCudaGrabParams->pNvFBCFrameGrabInfo = &frame_grab_info;
    fbcCudaGrabParams->dwFlags = NVFBC_TOCUDA_NOWAIT;
}

/* Grab a test frame here simply to get the pixel height and width to
 *  setup the encoder with */
int setup_encoder(Encoder* encoder,
                  NVFBC_CUDA_GRAB_FRAME_PARAMS* frame_grab_info,
                  CUdeviceptr frame_buffer) {
    if (NVFBC_SUCCESS != nvfbcCuda->NvFBCCudaGrabFrame(&fbcCudaGrabParams)) {
        fprintf(stderr, "ERROR: failed to grab test frame for encoder setup\n");
        status = EXIT_FAILURE;
        goto cleanup;
    }

    if (S_OK != encoder->SetupEncoder(frame_grab_info->dwWidth,
                                      frame_grab_info->dwHeight,
                                      frame_grab_info->dwBufferWidth,
                                      ENCODER_BITRATE)) {
        fprintf(stderr, "ERROR: failed setting up encoder\n");
        system.exit(EXIT_FAILURE);
    }
}



int main(int argc, char* argv[]) {
    // NvENC encoder class
    Encoder encoder;

    // Neccisary NvFBC structs
    NvFBCLibrary nvfbc_library;
    NvFBCCuda *nvfbc = NULL;
    NvFBCFrameGrabInfo frame_grab_info;
    NVFBCRESULT nvfbc_status = NVFBC_SUCCESS;

    CUcontext cuda_context = NULL;
    // Two CUDA dev points. One for the frame buffer in RGB and the other in
    // NV12 color space. NV12 is required for encoder
    CUdeviceptr frame_buffer_rgb = NULL,
                frame_buffer_nv12 = NULL;

    
    unsigned int frame_count = 0,
                 frame_idx = 0;
    int status = EXIT_SUCCESS;

    // Set to -1 to indicate no max width/height */
    DWORD maxDisplayWidth = -1,
          maxDisplayHeight = -1;
    DWORD maxBufferSize = -1;


    // Get reference to the current CUDA context
    checkCudaErrors(cuCtxPopCurrent(&cuda_context));

    // Creates an NvFBC class with shared system frame buffer
    // Using ARGB here for simplisity
    // TODO: move to YUV option
    nvfbcCuda = (NvFBCCuda*) nvfbc_library.create(NVFBC_SHARED_CUDA, &maxDisplayWidth, &maxDisplayHeight);
    if (!nvfbcCuda) {
        fprintf(stderr, "ERROR: failed to initialize NvFBC library\n");
        return EXIT_FAILURE;
    }

    // Allocate max buffer size here to avoid memory errors
    nvfbcCuda->NvFBCCudaGetMaxBufferSize(&maxBufferSize);
    checkCudaErrors(cuMemAlloc(&frame_buffer_rgb, maxBufferSize));
    checkCudaErrors(cuMemAlloc(&frame_buffer_nv12, maxBufferSize));
    
    // Set NvFBC parameters
    NVFBC_CUDA_SETUP_PARAMS fbcCudaSetupParams = {0};
    fbcCudaSetupParams.dwVersion = NVFBC_CUDA_SETUP_PARAMS_VER;
    fbcCudaSetupParams.eFormat = NVFBC_TOCUDA_ARGB;
    if(NVFBC_SUCCESS != nvfbcCuda->NvFBCCudaSetup(&fbcCudaSetupParams)) {
        fprintf(stderr, "ERROR: failed to initialize NvFBC\n");
        return EXIT_FAILURE;
    }
    init_frame_grab_params(&fbcCudaGrabParams, frame_grab_info, frame_buffer_rgb);

    
    // Set up the encoder
    if (S_OK != encoder.Init(cuda_context, maxBufferSize)) {
        fprintf(stderr, "ERROR: failed to initialize encoder\n");
        return EXIT_FAILURE;
    }
    setup_encoder(&encoder);


    // Main loop
    while (frame_count < NUM_FRAMES_TO_RECORD) {

        // Grab a frame
        if (NVFBC_SUCCESS != nvfbcCuda->NvFBCCudaGrabFrame(&fbcCudaGrabParams)) {
            fprintf(stderr, "ERROR: failed to grab frame\n");
            status = EXIT_FAILURE;
            goto cleanup;
        }

        // Transform ARGB to NV12 color space
        launch_CudaARGB2NV12Process(frame_grab_info.dwBufferWidth,
                                    frame_grab_info.dwHeight,
                                    frame_buffer_rgb,
                                    frame_buffer_nv12);

        // Attempt to encode the frame
        frame_idx = frame_count % MAX_BUF_QUEUE;
        if(S_OK != encoder.LaunchEncode(frame_idx, frame_buffer_nv12)) {
            fprintf(stderr, "ERROR: failed to encode frame %d\n", frame_count);
            status = EXIT_FAILURE;
            goto cleanup;
        }

        // Get bit stream from encoder
        if(S_OK != encoder.GetBitstream(frame_idx, fOut)) {
            fprintf(stderr, "ERROR: failed to encode frame %d\n", frame_count);
            status = EXIT_FAILURE;
            goto cleanup;
        }

        frame_count++;
    }


 cleanup:
    encoder.TearDown();
    nvfbcCuda->NvFBCCudaRelease();

    return status;
}
