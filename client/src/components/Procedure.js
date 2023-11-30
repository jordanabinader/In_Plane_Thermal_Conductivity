
  export default function Procedure() {
    return (
      <div className="bg-white">
        <div className="mx-auto grid max-w-2xl grid-cols-1 items-center gap-x-8 gap-y-16 px-4 py-24 sm:px-6 sm:py-32 lg:max-w-7xl lg:grid-cols-2 lg:px-8">
            <div>
                <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Procedure</h2>
                <p className="mt-4 text-gray-500">
                The Ångström method procedure...
                </p>
  
                <dl className="mt-16 grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-2 sm:gap-y-16 lg:gap-x-8">
                    <div className="border-t border-gray-200 pt-4">
                        <dt className="font-medium text-red-600">1 - Lift the clamp blocks</dt>
                        <dd className="mt-2 text-sm text-gray-500">Remove the thumb screw and lift the clamp blockson both sides. Fix them using... </dd>
                    </div>
                    <div className="border-t border-gray-200 pt-4">
                        <dt className="font-medium text-red-600">2 - Mount the sample</dt>
                        <dd className="mt-2 text-sm text-gray-500">Align sample with clamping... </dd>  
                    </div>
                    <div className="border-t border-gray-200 pt-4">
                        <dt className="font-medium text-red-600">3 - Tighted the clamps</dt>
                        <dd className="mt-2 text-sm text-gray-500">Adjust with spring and spacer blocks... </dd>  
                    </div>
                    <div className="border-t border-gray-200 pt-4">
                        <dt className="font-medium text-red-600">4 - Set the thermocouples</dt>
                        <dd className="mt-2 text-sm text-gray-500">Adjust TC distance with standoffs... </dd>  
                    </div>
                </dl>
            </div>
            <img
                src="Picture1.png"
                className="rounded-lg bg-gray-100"
            />
        </div>
      </div>
    )
  }
